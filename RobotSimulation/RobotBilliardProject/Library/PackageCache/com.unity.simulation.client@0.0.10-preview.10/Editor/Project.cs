using System;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Reflection;

#if UNITY_EDITOR
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Networking;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.IMGUI.Controls;
using ZipUtility;

using Debug = UnityEngine.Debug;

namespace Unity.Simulation.Client
{
    /// <summary>
    /// Class for retrieving project, scenes, and building a project for uploading.
    /// </summary>
    public static class Project
    {
        // Public Members

        /// <summary>
        /// State for project id and client readiness.
        /// This state starts as Pending and will either become Valid or Invalid depending on
        /// whether or not the Unity project id  has been linked in the Cloud Services window / client readiness is valid.
        /// </summary>
        public enum State
        {
            /// <summary>
            /// The state is pending / unknown.
            /// </summary>
            Pending,

            /// <summary>
            /// The state is invalid, i.e. the project id is invalid, and hence the client is not ready.
            /// </summary>
            Invalid,

            /// <summary>
            /// The state is valid, and the client is ready.
            /// All API calls will work as intended.
            /// </summary>
            Valid
        }

        /// <summary>
        /// Thread safe accessor for CloudProjectSettings.accessToken
        /// </summary>
        public static string accessToken { get; private set; }

        /// <summary>
        /// Delegate for access token change events.
        /// </summary>
        public delegate void AccessTokenChangedDelegate(State state);

        /// <summary>
        /// Event for subscribing to access token changes.
        /// </summary>
        public static event AccessTokenChangedDelegate accessTokenChanged;

        /// <summary>
        /// Determines the state of the access token.
        /// Not having an access token, and calling API methods will result in exceptions being thrown.
        /// </summary>
        /// <returns> True if a valid cloud project id is linked. </returns>
        public static State accessTokenState { get; private set; } = State.Pending;


        /// <summary>
        /// Returns the currently active project id.
        /// </summary>
        public static string activeProjectId { get; private set; }

        /// <summary>
        /// Delegate type for informing project id state changes.
        /// </summary>
        public delegate void ProjectIdChangedDelegate(State state);

        /// <summary>
        /// Event for subscribing to project id changes.
        /// </summary>
        public static event ProjectIdChangedDelegate projectIdChanged;

        /// <summary>
        /// Determines the state of the Unity project id, which is needed for API calls.
        /// Not having a linked cloud project id, and calling API methods will result in exceptions being thrown.
        /// </summary>
        /// <returns> True if a valid cloud project id is linked. </returns>
        public static State projectIdState { get; private set; } = State.Pending;


        /// <summary>
        /// Returns the current client readiness.
        /// </summary>
        public static bool clientReady { get; private set; }

        /// <summary>
        /// Delegate type for informing when the client library is ready to use.
        /// </summary>
        public delegate void ClientReadyDelegate(State state);

        /// <summary>
        /// Event for subscribing to client ready state changes.
        /// </summary>
        public static event ClientReadyDelegate clientReadyStateChanged;

        /// <summary>
        /// Determines the ready state of the simulation client API.
        /// Calling API methods before the client is ready will result in exceptions being thrown.
        /// </summary>
        /// <returns> True if the client is in a ready state. </returns>
        public static State clientReadyState { get; private set; } = State.Pending;

        /// <summary>
        /// Retrieves a list of the projects you have created.
        /// </summary>
        /// <returns> An array of ProjectInfo structs. </returns>
        public static ProjectInfo[] GetProjects(string accessToken = null)
        {
            var url = Config.apiEndpoint + "/v1/projects";

            using (var message = new HttpRequestMessage(HttpMethod.Get, url))
            {
                Transaction.SetAuthHeaders(message.Headers, accessToken);
                var request = Transaction.client.SendAsync(message);
                request.Wait(TimeSpan.FromSeconds(Config.timeoutSecs));

                if (!request.Result.IsSuccessStatusCode)
                {
                    throw new Exception("GetProjects failed " + request.Result.ReasonPhrase);
                }

                var payload = request.Result.Content.ReadAsStringAsync();
                payload.Wait();

                var array = JsonUtility.FromJson<ProjectArray>(payload.Result);
                return array.projects;
            }
        }

        /// <summary>
        /// Sets the active project id to the value specified.
        /// If no project id is specified, then the current project Cloud Project Id is used.
        /// Generally you should not need to ever use this method. It is meant to force the
        /// project id to a specific value. 
        /// Setting this to a value other than the CloudProjectSettings.projectId or null, may
        /// result in the events accessTokenChanged, projectIdChanged, and clientReadyStateChanged
        /// not working as expected.
        /// </summary>
        public static void Activate(string projectId = null)
        {
            if (!string.IsNullOrEmpty(projectId) && projectId != CloudProjectSettings.projectId)
            {
                activeProjectId = projectId;
                _projectActivated = true;
            }
            else
            {
                activeProjectId = CloudProjectSettings.projectId;
            }
        }

        /// <summary>
        /// Deactivates the currently active project id.
        /// </summary>
        public static void Deactivate()
        {
            activeProjectId = null;
            _projectActivated = false;
        }

        /// <summary>
        /// Retrieves a list of the scenes you currently have open in the editor.
        /// </summary>
        public static string[] GetOpenScenes()
        {
            var countLoaded = SceneManager.sceneCount;
            var loadedScenes = new string[countLoaded];
            for (int i = 0; i < countLoaded; i++)
                loadedScenes[i] = SceneManager.GetSceneAt(i).path;
            return loadedScenes;
        }

        /// <summary>
        /// Retrieves a list of the scenes that are currently added to the build in build settings.
        /// </summary>
        public static string[] GetBuildSettingScenes()
        {
            var countLoaded = SceneManager.sceneCountInBuildSettings;
            var loadedScenes = new string[countLoaded];
            for (int i = 0; i < countLoaded; i++)
                loadedScenes[i] = SceneManager.GetSceneByBuildIndex(i).path;
            return loadedScenes;
        }

        /// <summary>
        /// Builds the current project.
        /// </summary>
        /// <param name="savePath"> The location where the build should be saved. Note that a new directory will be created at this location. </param>
        /// <param name="name"> Name for the build directory and executable. </param>
        /// <param name="scenes"> Array of scenes to be included in the build. </param>
        /// <param name="target"> The build target to build for. Defaults to StandaloneLinux64 </param>
        /// <param name="compress"> Flag for whether or not to compress the build executable and data directory into a zip file. </param>
        /// <param name="launch"> Flag for whether or not to launch the build. </param>
        public static bool BuildProject(string savePath, string name, string[] scenes = null, BuildTarget target = BuildTarget.StandaloneLinux64, BuildOptions buildOptions = BuildOptions.None, bool compress = true, bool launch = false)
        {
            Directory.CreateDirectory(savePath);

            BuildPlayerOptions buildPlayerOptions = new BuildPlayerOptions();
            buildPlayerOptions.locationPathName = Path.Combine(savePath, name + ".x86_64");
            buildPlayerOptions.target           = target;
            buildPlayerOptions.options          = buildOptions;
            buildPlayerOptions.scenes           = scenes;

            BuildReport  report  = BuildPipeline.BuildPlayer(buildPlayerOptions);
            BuildSummary summary = report.summary;

            if (summary.result == BuildResult.Succeeded)
            {
                Debug.Log("Build succeeded: " + summary.totalSize + " bytes");
            }

            if (summary.result == BuildResult.Failed)
            {
                Debug.Log("Build failed");
                return false;
            }

            if (launch)
            {
                var exe = Path.Combine(Application.dataPath, "..", savePath + ".app");
                Debug.Log("Executing " + exe);
                Process.Start(exe);
            }

            if (compress)
                Zip.DirectoryContents(savePath, name);

            return true;
        }

        /// <summary>
        /// Returns the appropriate BuildTarget for building a standalone player to match the editor you are using.
        /// </summary>
        /// <returns> BuildTarget </returns>
        public static BuildTarget StandaloneBuildTargetForEditor()
        {
#if UNITY_EDITOR_WIN
            return BuildTarget.StandaloneWindows;
#elif UNITY_EDITOR_OSX
            return BuildTarget.StandaloneOSX;
#elif UNITY_EDITOR_LINUX
            return BuildTarget.StandaloneLinux64;
#else
            Debug.Assert(false, "Unsupported BuildTarget");
            return null;
#endif
        }

        // Protected / Private Members

        internal static void ValidateProjectId()
        {
            if (string.IsNullOrEmpty(activeProjectId))
            {
                throw new InvalidOperationException("Project.activeProjectId is invalid. You must either create a new Unity project id, or link your project to an existing Unity project id in the Cloud Services window.");
            }
        }
        
        public static void SetAccessToken(string accessToken)
        {
            Transaction.accessToken = accessToken;
        }

        const float TimeBeforeDeclaringInvalidStateInMilliseconds = 3000;

        static bool _projectActivated = false;
        static Stopwatch _timer = new Stopwatch();

        static object _ucInstance = GetUnityConnectInstance();

        [InitializeOnLoadMethod]
        static void Initialize()
        {
            _timer.Start();
            EditorApplication.update += () =>
            {
                var oldProjectIdState = projectIdState;
                var oldTokenState     = accessTokenState;
                var oldReadyState     = clientReadyState;

                // Project Id State.

                if (LoggedIn() && !string.IsNullOrEmpty(CloudProjectSettings.projectId))
                {
                    if (!_projectActivated)
                        activeProjectId = CloudProjectSettings.projectId;
                    
                    if (!string.IsNullOrEmpty(activeProjectId))
                        projectIdState = State.Valid;
                }

                // Token State.

                if (!string.IsNullOrEmpty(CloudProjectSettings.accessToken))
                {
                    accessToken = CloudProjectSettings.accessToken;
                    accessTokenState = State.Valid;
                }

                // Client Readiness

                if (projectIdState == State.Valid && accessTokenState == State.Valid)
                {
                    clientReady = true;
                    clientReadyState = State.Valid;
                }

                // Timeout

                if (_timer.Elapsed.TotalMilliseconds > TimeBeforeDeclaringInvalidStateInMilliseconds)
                {
                    if (_projectActivated)
                        return;
                    
                    if (string.IsNullOrEmpty(CloudProjectSettings.projectId))
                    {
                        activeProjectId = null;
                        projectIdState = State.Invalid;
                    }
                    else
                    {
                        activeProjectId = CloudProjectSettings.projectId;
                        projectIdState = State.Valid;
                    }

                    if (string.IsNullOrEmpty(CloudProjectSettings.accessToken))
                    {
                        accessToken = null;
                        accessTokenState = State.Invalid;
                    }

                    if (projectIdState == State.Invalid || accessTokenState == State.Invalid)
                    {
                        clientReady = false;
                        clientReadyState = State.Invalid;
                    }
                }

                // Notifications

                if (oldProjectIdState != projectIdState)
                {
                    projectIdChanged?.Invoke(projectIdState);
                }
                
                if (oldTokenState != accessTokenState)
                {
                    accessTokenChanged?.Invoke(accessTokenState);
                }

                if (oldReadyState != clientReadyState)
                {
                    clientReadyStateChanged?.Invoke(clientReadyState);
                }
            };
        }

        internal static object GetUnityConnectInstance()
        {
            foreach(var assembly in AppDomain.CurrentDomain.GetAssemblies())
                foreach(var t in assembly.GetTypes())
                    if (t.FullName == "UnityEditor.Connect.UnityConnect")
                        return t.GetProperty("instance")?.GetGetMethod()?.Invoke(null, null);
            return null;
        }

        internal static bool LoggedIn()
        {
            return _ucInstance == null ? false : (bool)_ucInstance.GetType().GetProperty("loggedIn").GetGetMethod().Invoke(_ucInstance, null);
        }
    }
}
#endif // UNITY_EDITOR
