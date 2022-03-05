using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

using UnityEditor;
using UnityEditorInternal;
using UnityEditor.Build.Reporting;

using UnityEngine;

using Unity.Simulation;
using ZipUtility;

namespace Unity.Simulation.Client
{
    [Serializable]
    public class AppParamInfo
    {
        public string           name = "App Param";
        public ScriptableObject appParam;
        public int              instanceCount = 1;
        internal bool           isExpanded = true;
        internal bool           expandJson = false;
        internal bool           hasError   = false;
        internal string         json;
        internal int            jsonLineCount;
    }

    [Serializable]
    public class SceneInfo
    {
        public SceneAsset scene;
        internal bool     hasError = false;
    }

    public class CreateBuildEditorWindow : EditorWindow
    {
#if UNITY_SIMULATION_ENABLE_RUN_IN_SIMULATION
        [MenuItem("Window/Simulation/Run in Unity Simulation")]
        static void ShowWindow()
        {
            var window = GetWindow<CreateBuildEditorWindow>();
            window.titleContent = new GUIContent("Run in Unity Simulation");
            window.Show();
        }
#endif

        Vector2                 _scrollPosition;
        string                  _runName;
        string                  _runDescription;
        bool                    _useExistingBuildId;
        string                  _existingBuildId;
        string                  _buildLocation;
        string                  _buildName;
        string                  _buildZipPath;
        bool                    _developmentBuild;
        string[]                _availableBuildTargets;
        int                     _buildTargetIndex;

        AppParamListEditor      _appParamListEditor;
        List<AppParam>          _appParamList;

        SceneListEditor         _sceneListEditor;
        List<string>            _sceneNamesList;

        bool                    _systemParametersFetched = false;
        SysParamDefinition[]    _systemParameters;
        string[]                _systemParameterDescriptions;
        int                     _systemParameterIndex;

        float                   _progress;
        string                  _progressStatus;
        Task<Run>               _executionTask;
        string                  _runExecutionId;
        CancellationTokenSource _cancellationTokenSource;
        bool                    _progressBarDirty;

        void OnEnable()
        {
            _appParamListEditor = new AppParamListEditor();
            _sceneListEditor    = new SceneListEditor();

            _runName        = "RunName";
            _runDescription = "";
            _buildLocation  = $"{new DirectoryInfo(Application.dataPath).Parent.FullName}{Path.DirectorySeparatorChar}Build";
            _buildName      = Application.productName;

            _availableBuildTargets = new string[]
            {
                BuildTarget.StandaloneLinux64.ToString()
#if PLATFORM_CLOUD_RENDERING
               ,BuildTarget.CloudRendering.ToString()
#endif
            };
#if PLATFORM_CLOUD_RENDERING
            _buildTargetIndex = 1;
#endif

            Project.Activate();
            Project.clientReadyStateChanged += OnClientReadyStateChanged;

            AssemblyReloadEvents.beforeAssemblyReload += () =>
            {
                if (_executionTask != null)
                    EditorUtility.ClearProgressBar();
            };
        }

        public void OnDestroy()
        {
            Project.projectIdChanged -= OnClientReadyStateChanged;
            if (_cancellationTokenSource != null)
            {
                _cancellationTokenSource.Cancel();
                EditorUtility.ClearProgressBar();
            }
        }

        public void OnGUI()
        {
            if (Project.projectIdState == Project.State.Pending)
            {
                EditorGUILayout.LabelField("Waiting for connection to Unity Cloud.");
                return;
            }
            else if (Project.projectIdState == Project.State.Invalid)
            {
                EditorGUILayout.LabelField("Project must be associated with a valid Unity Cloud project to run in Unity Simulation.");
                return;
            }

            if (!_systemParametersFetched)
            {
                _systemParametersFetched = true;
                Task.Run(() =>
                {
                    _systemParameters = API.GetSysParams();
                    _systemParameterDescriptions = _systemParameters.Where(s => s.allowed).Select(s => s.description).ToArray();
                });
            }

            // Run Info

            _runName = EditorGUILayout.TextField("Run Name", _runName);
            _runDescription = EditorGUILayout.TextField("Run Description", _runDescription);

            EditorGUILayout.Space();

            // Build Info

            _useExistingBuildId = EditorGUILayout.Toggle("Use Existing Build Id", _useExistingBuildId);
            if (_useExistingBuildId)
            {
                _existingBuildId = EditorGUILayout.TextField("Existing Build Id", _existingBuildId);
            }
            else
            {
                _buildLocation    = EditorGUILayout.TextField("Build Location", _buildLocation);
                _buildName        = EditorGUILayout.TextField("Build Name", _buildName);
                _developmentBuild = EditorGUILayout.Toggle("Development Build", _developmentBuild);

                if (_availableBuildTargets.Length > 1)
                    _buildTargetIndex = EditorGUILayout.Popup("Build Target", _buildTargetIndex, _availableBuildTargets);
            }

            EditorGUILayout.Space();

            // System Parameters

            if (_systemParameterDescriptions == null)
                EditorGUILayout.LabelField("System Parameter", "Waiting for system parameters from Unity Simulation Service.");
            else
                _systemParameterIndex = EditorGUILayout.Popup("System Parameter", _systemParameterIndex, _systemParameterDescriptions);

            EditorGUILayout.Space();
            EditorGUILayout.Space();

            _scrollPosition = EditorGUILayout.BeginScrollView(_scrollPosition);

            // Application Parameters

            _appParamListEditor.OnGUI();

            // Scene Selections

            EditorGUILayout.Space();

            _sceneListEditor.OnGUI();

            EditorGUILayout.EndScrollView();

            // Build and Execute

            EditorGUILayout.Space();

            // Validate Build and Execute Options
            GUI.enabled = ValidateAllOptions();

            // Build and Execute

            if (GUILayout.Button("Build & Execute"))
            {
                _sceneNamesList = _sceneListEditor.scenes.Select(si => AssetDatabase.GetAssetPath(si.scene)).ToList();

                // batch upload of app params.
                var batch = new Dictionary<string, object>(_appParamListEditor.appParams.Count);
                foreach (var ap in _appParamListEditor.appParams)
                    batch.Add(ap.name, ap.appParam);

                var appParamIds = API.UploadAppParamBatch(batch);
                Debug.Assert(appParamIds.Count == _appParamListEditor.appParams.Count);

                _appParamList = new List<AppParam>(_appParamListEditor.appParams.Count);
                foreach (var ap in _appParamListEditor.appParams)
                {
                    Debug.Assert(appParamIds.ContainsKey(ap.name));
                    _appParamList.Add(new AppParam()
                    {
                        id            = appParamIds[ap.name],
                        name          = ap.name,
                        num_instances = ap.instanceCount
                    });
                }

                UpdateProgress(0f, "");

                _cancellationTokenSource = new CancellationTokenSource();

                if (_useExistingBuildId)
                {
                    _executionTask = new Task<Run>(() => ExecuteRun(_buildName, _systemParameters[_systemParameterIndex].id, _cancellationTokenSource.Token, _existingBuildId));
                    _executionTask.Start();
                }
                else
                {
                    _executionTask = BuildAndExecuteRun(_buildName, _systemParameters[_systemParameterIndex].id);
                }
                _executionTask?.ContinueWith(task => _runExecutionId = task.Result.executionId);
            }

            GUI.enabled = true;
        }

        bool ValidateAllOptions()
        {
            if (string.IsNullOrEmpty(_runName))
                return false;
            if (_useExistingBuildId && string.IsNullOrEmpty(_existingBuildId))
                return false;
            if (_appParamListEditor.appParams.Count <= 0)
                return false;
            if (_sceneListEditor.scenes.Count <= 0)
                return false;
            foreach (var ap in _appParamListEditor.appParams)
                if (ap.hasError)
                    return false;
            foreach (var scn in _sceneListEditor.scenes)
                if (scn.hasError)
                    return false;
            return true;
        }

        void OnClientReadyStateChanged(Project.State state)
        {
            Repaint();
        }

        public void Update()
        {
            if (_executionTask == null)
                return;

            if (_executionTask.IsCompleted)
            {
                EditorUtility.ClearProgressBar();
                _executionTask = null;
                return;
            }

            if (_progressBarDirty && EditorUtility.DisplayCancelableProgressBar("Run in Unity Simulation", _progressStatus, _progress))
            {
                _progressBarDirty = false;
                _cancellationTokenSource?.Cancel();
                _cancellationTokenSource = null;
            }

            Repaint();
        }

        public Task<Run> BuildAndExecuteRun(string _runName, string sysParamId)
        {
            var token = _cancellationTokenSource.Token;

#if PLATFORM_CLOUD_RENDERING
            var target = BuildTarget.CloudRendering;
#else
            var target = BuildTarget.StandaloneLinux64;
#endif
            var buildSuccess = Project.BuildProject(_buildLocation, _buildName, _sceneNamesList.ToArray(), target, _developmentBuild ? BuildOptions.Development : BuildOptions.None, compress: true);
            if (!buildSuccess)
                return null;

            _buildZipPath = Path.Combine(Directory.GetParent(_buildLocation).FullName, $"{_buildName}.zip");
            var taskRun = API.UploadBuildAsync(_runName, _buildZipPath, cancellationTokenSource: _cancellationTokenSource, progress: progress =>
            {
                UpdateProgress(progress, "Uploading Build");
            });

            var _executionTask = taskRun.ContinueWith(finishedTask =>
            {
                _cancellationTokenSource = null;

                if (finishedTask.IsCanceled)
                    return null;

                if (finishedTask.IsFaulted)
                {
                    Debug.LogError($"Upload failed. {finishedTask.Exception}");
                    return null;
                }

                Debug.Log($"Upload complete: build id {finishedTask.Result}");

                return ExecuteRun(_runName, sysParamId, token, finishedTask.Result);
            },
            token);

            return _executionTask;
        }

        Run ExecuteRun(string _runName, string sysParamId, CancellationToken token, string buildId)
        {
            UpdateProgress(1f, "Executing Run");

            var runDefinitionId = API.UploadRunDefinition(new RunDefinition
            {
                app_params   = _appParamList.ToArray(),
                name         = _runName,
                sys_param_id = sysParamId,
                build_id     = buildId
            });

            var run = Run.CreateFromDefinitionId(runDefinitionId);
            run.Execute();

            _cancellationTokenSource.Dispose();

            return run;
        }

        void UpdateProgress(float progress, string status = "")
        {
            _progressStatus   = status;
            _progress         = progress;
            _progressBarDirty = true;
        }
    }
}
