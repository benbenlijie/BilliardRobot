using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Runtime.CompilerServices;
using System.Threading;

#if UNITY_EDITOR
using UnityEngine;
using UnityEngine.Networking;
using UnityEditor;
#endif

namespace Unity.Simulation.Client
{
    
    [InitializeOnLoad]
    public class Run
    {
        // Public Members

        /// <summary>
        /// Delegate type for receiving notification when a run completes.
        /// </summary>
        public delegate void RunCompletedDelegate(Run run);

        /// <summary>
        /// Event to receive notification when a run completes.
        /// </summary>
        public event RunCompletedDelegate runCompleted;

        /// <summary>
        /// Returns the run definition id.
        /// </summary>
        public string definitionId { get; protected set; }

        /// <summary>
        /// Returns the run execution id.
        /// </summary>
        public string executionId { get; protected set; }

        /// <summary>
        /// Set/Get the build location for this run.
        /// </summary>
        public string buildLocation { get; set; }

        /// <summary>
        /// Returns the total number of instances for this run.
        /// </summary>
        public int instances { get; protected set; }

        /// <summary>
        /// Returns true when all instances have completed.
        /// Note that completed and success are not the same thing. 
        /// </summary>
        public bool completed { get; protected set; }

        /// <summary>
        /// Returns the run summary for this run.
        /// When a run is executing, it will periodically update the run summary.
        /// When this occurs is not guaranteed until after completion.
        /// </summary>
        public RunSummary summary { get; protected set; }

        /// <summary>
        /// Map of currently uploaded app parameters for this run.
        /// </summary>
        public Dictionary<string, AppParam> appParameters = new Dictionary<string, AppParam>();

        static Run()
        {
            _Initialize();
        }

        /// <summary>
        /// Create a new run definition.
        /// </summary>
        /// <param name="name"> Name for this run. </param>
        /// <param name="description"> Description text for this run. </param>
        public static Run Create(string name = null, string description = null, string accessToken = null)
        {
            var run = new Run();
            run._definition.name = name;
            run._definition.description = description;
#if UNITY_EDITOR
            if (string.IsNullOrEmpty(accessToken))
                accessToken = Project.accessToken;
#endif
            run._accessToken = accessToken;
            return run;
        }

        /// <summary>
        /// Create a run definition instance from a previously uploaded run definition.
        /// </summary>
        /// <param name="definitionId"> The run definition id returned from a previous upload. </param>
        public static Run CreateFromDefinitionId(string definitionId, string accessToken = null)
        {
            var run = new Run();
            run.definitionId = definitionId;
            run._definition = API.DownloadRunDefinition(definitionId);
#if UNITY_EDITOR
            if (string.IsNullOrEmpty(accessToken))
                accessToken = Project.accessToken;
#endif
            run._accessToken = accessToken;
            return run;
        }

        /// <summary>
        /// Create a run definition instance from a previously uploaded run execution.
        /// </summary>
        /// <param name="executionId"> The run execution id returned from a previous run. </param>
        public static Run CreateFromExecutionId(string executionId, string accessToken = null)
        {
            var run = new Run();
            var description  = API.Describe(executionId);
            run._definition  = _DescriptionToDefinition(description);
            run.executionId  = executionId;
            run.definitionId = description.definition_id;
#if UNITY_EDITOR
            if (string.IsNullOrEmpty(accessToken))
                accessToken = Project.accessToken;
#endif
            run._accessToken = accessToken;
            return run;
        }

        /// <summary>
        /// Set the sys parameter to be used for this run.
        /// </summary>
        /// <param name="sysParam"> The sys param selected from GetSysParam. </param>
        public void SetSysParam(SysParamDefinition sysParam)
        {
            _sysParam = sysParam;
        }

        /// <summary>
        /// Sets the build location that will be uploaded.
        /// </summary>
        /// <param name="path"> The path to the zipped up build to be uploaded. </param>
        public void SetBuildLocation(string path)
        {
            buildLocation = path;
        }

        /// <summary>
        /// Sets the build id of a previously uploaded build.
        /// </summary>
        /// <param name="id"> The id of a previously uploaded build. </param>
        public void SetBuildId(string id)
        {
            _definition.build_id = id;
        }

        /// <summary>
        /// Add an app param to be uploaded. Struct T will be converted to JSON.
        /// </summary>
        /// <param name="name"> Name for the app param. </param>
        /// <param name="param"> Struct value to be converted to JSON and uploaded. </param>
        /// <param name="numInstances"> The number of instances to use this app param. </param>
        public string SetAppParam<T>(string name, T param, int numInstances, string accessToken = null)
        {
            AppParam appParam;
            appParam.id            = API.UploadAppParam<T>(name, param, accessToken);
            appParam.name          = name;
            appParam.num_instances = numInstances;

            if (!appParameters.ContainsKey(name))
            {
                instances += numInstances;
                appParameters.Add(name, appParam);
            }
            else
            {
                appParameters[name] = appParam;
            }

            Debug.Log($"AppParam {appParam.id} numInstances {appParam.num_instances}");

            return appParam.id;
        }
        
        /// <summary>
        /// Add an app param to be uploaded..
        /// </summary>
        /// <param name="name"> Name for the app param. </param>
        /// <param name="param"> Json string appParam to be uploaded. </param>
        /// <param name="numInstances"> The number of instances to use this app param. </param>
        public string SetAppParam(string name, string param, int numInstances, string accessToken = null)
        {
            Debug.Assert(param.EndsWith("}") && param.StartsWith("{"), "Not a json string");
            
            AppParam appParam;
            appParam.id            = API.UploadAppParam(name, param, accessToken);
            appParam.name          = name;
            appParam.num_instances = numInstances;

            if (!appParameters.ContainsKey(name))
            {
                instances += numInstances;
                appParameters.Add(name, appParam);
            }
            else
            {
                appParameters[name] = appParam;
            }

            Debug.Log($"AppParam {appParam.id} numInstances {appParam.num_instances}");

            return appParam.id;
        }

        /// <summary>
        /// Get a previously added app param.
        /// </summary>
        /// <param name="name"> Name of previously added app param. </param>
        public T GetAppParam<T>(string name, string accessToken = null) where T : struct
        {
            if (appParameters.ContainsKey(name))
            {
                var appParam = appParameters[name];
                return _GetAppParam<T>(appParam.id, accessToken);
            }
            return default(T);
        }

        /// <summary>
        /// Executes this run definition.
        /// </summary>
        public void Execute(string accessToken = null)
        {
#if UNITY_EDITOR
            Project.ValidateProjectId();
#endif

            if (string.IsNullOrEmpty(_definition.build_id) && string.IsNullOrEmpty(buildLocation))
            {
                throw new ArgumentException("Both the build id and build location are undefined. You must specify either a build id or a build location before executing the run.");
            }

            // Upload Build
            if (string.IsNullOrEmpty(_definition.build_id))
            {
                _definition.build_id = API.UploadBuild(_definition.name, buildLocation, Transaction.accessToken);
                Debug.Log("Build id " + _definition.build_id);
            }

            if (string.IsNullOrEmpty(definitionId))
            {
                // Upload Run Definition
                _definition.sys_param_id = _sysParam.id;
                _definition.app_params   = new List<AppParam>(appParameters.Values).ToArray();
                definitionId = API.UploadRunDefinition(_definition, accessToken);
                Debug.Log("Definition Id " + definitionId);
            }

            // Execute
            var runUrl = $"{Config.apiEndpoint}/v1/projects/{Project.activeProjectId}/runs";
            using (var message = new HttpRequestMessage(HttpMethod.Post, runUrl))
            {
                RunDefinitionId rdid;
                rdid.definition_id = definitionId;

                Transaction.SetAuthHeaders(message.Headers, _accessToken);
                message.Content = new StringContent(JsonUtility.ToJson(rdid), Encoding.UTF8, "application/json");
                var request = Transaction.client.SendAsync(message);
                request.Wait(TimeSpan.FromSeconds(Config.timeoutSecs));

                if (!request.Result.IsSuccessStatusCode)
                {
                    throw new Exception("Execute failed " + request.Result.ReasonPhrase);
                }

                var payload = request.Result.Content.ReadAsStringAsync();
                payload.Wait();

                var response = JsonUtility.FromJson<RunExecutionId>(payload.Result);
                executionId = response.execution_id;

#if UNITY_EDITOR
                // Currently there's an issue where if you upload app-params using API.UploadAppParam() then the number
                // of instances is not set, so the run will complete immediately. In order to use run.completed you must
                // upload app-params using run.SetAppParam().
                if (instances > 0)
                    _Monitor(this);
#endif

                Debug.Log("Execution Id " + executionId);
            }
        }

        /// <summary>
        /// Retrieves the player log for a specific instance.
        /// </summary>
        /// <param name="instance"> The instance whose player log you wish to retrieve. Defaults to 1.</param>
        public string[] GetPlayerLog(int instance = 1, string accessToken = null)
        {
            var manifest = API.GetManifest(executionId);
            foreach (var kv in manifest)
            {
                if (kv.Value.instanceId == instance && kv.Value.fileName == "Logs/Player.Log")
                {
                    return Encoding.UTF8.GetString(_GetManifestEntry(kv.Value, accessToken)).Split(Environment.NewLine.ToCharArray(), StringSplitOptions.RemoveEmptyEntries);
                }
            }
            return null;
        }

        // Protected / Private Members

        Run()
        {
#if UNITY_EDITOR
            _accessToken = Project.accessToken;
#endif
        }

        byte[] _GetManifestEntry(ManifestEntry entry, string accessToken)
        {
            using (var message = new HttpRequestMessage(HttpMethod.Get, entry.downloadUri))
            {
                Transaction.SetAuthHeaders(message.Headers, accessToken);
                var request = Transaction.client.SendAsync(message);
                request.Wait(TimeSpan.FromSeconds(Config.timeoutSecs));

                if (!request.Result.IsSuccessStatusCode)
                {
                    throw new Exception("_GetManifestEntry: failed " + request.Result.ReasonPhrase);
                }

                var payload = request.Result.Content.ReadAsByteArrayAsync();
                payload.Wait();

                return payload.Result;
            }
        }

        static T _GetAppParam<T>(string id, string accessToken)
        {
            Project.ValidateProjectId();
            var url  = $"{Config.apiEndpoint}/v1/projects/{Project.activeProjectId}/app_params";
            var data = Transaction.Download(url, id, true, accessToken);
            return JsonUtility.FromJson<T>(Encoding.UTF8.GetString(data));
        }

        static RunDefinition _DescriptionToDefinition(RunDescription description)
        {
            RunDefinition definition;
            definition.name         = description.name;
            definition.description  = description.description;
            definition.build_id     = description.build_id;
            definition.sys_param_id = description.sys_param_id;
            definition.app_params   = description.app_params;
            return definition;
        }

        SysParamDefinition _sysParam;
        RunDefinition      _definition;
        float _monitorElapsedTime;

#if UNITY_EDITOR
        string _accessToken;

        static int kMonitorSleepTimeInMilliseconds = 5000;

        static List<Run> _runsInProgress = new List<Run>();
        static List<Run> _runsCompleted  = new List<Run>();

        static Thread    _thread;
        static bool      _running = true;

        [RuntimeInitializeOnLoadMethod]
        static void _Initialize()
        {
            Application.quitting += () =>
            {
                _running = false;
                _thread?.Join();
                _thread = null;
            };
            
            AssemblyReloadEvents.beforeAssemblyReload += () =>
            {
                if (_thread != null)
                {
                    _running = false;
                    _thread.Join();
                }
            };

            EditorApplication.update += () =>
            {
                lock (_runsInProgress)
                {
                    foreach (var run in _runsInProgress)
                    {
                        var completedInstances = run.summary.num_failures + run.summary.num_not_run + run.summary.num_success;
                        if (completedInstances == run.instances)
                        {
                            run.completed = true;
                            _runsCompleted.Add(run);
                        }
                    }

                    foreach (var run in _runsCompleted)
                        _runsInProgress.Remove(run);
                }

                // Dispatch event outside of lock to avoid holding lock for lengthy period.
                foreach (var run in _runsCompleted)
                {
                    Debug.Log($"Run {run.executionId} num_success {run.summary.num_success} failures {run.summary.num_failures} completed {run.completed}");
                    run.runCompleted?.Invoke(run);
                }
                _runsCompleted.Clear();
            };

            _thread = new Thread(new ThreadStart(() =>
            {
                while (_running)
                {
                    try
                    {
                        Run[] runs = null;
                        lock (_runsInProgress) { runs = _runsInProgress.ToArray(); }

                        // Summarize run for each non completed run.
                        // Ignore atomicity of run.summary assignment. Summary is not guaranteed to be valid until after run.completed is true.
                        // In worst case, code path that sets run.completed to true will execute for one additional update.
                        foreach (var run in runs)
                            if (!run.completed)
                                run.summary = API.Summarize(run.executionId, run._accessToken);

                        Thread.Sleep(kMonitorSleepTimeInMilliseconds);
                    }
                    catch (Exception e)
                    {
                        // This can happen on a domain reload, which will kill the thread and start a new one.
                        if (e is ThreadAbortException)
                        {
                            return;
                        }

                        Debug.LogError($"Run monitor unhandled exception : {e.Message}");

                        throw;
                    }
                }
            }));
            _thread.Start();
        }

        static void _Monitor(Run run)
        {
            lock (_runsInProgress)
            {
                Debug.Assert(_runsInProgress.IndexOf(run) < 0, $"Run {run.executionId} is already being monitored.");
                _runsInProgress.Add(run);
                Debug.Log($"Added run {run.executionId} to monitored runs");
            }
        }
#endif // UNITY_EDITOR
    }
}
