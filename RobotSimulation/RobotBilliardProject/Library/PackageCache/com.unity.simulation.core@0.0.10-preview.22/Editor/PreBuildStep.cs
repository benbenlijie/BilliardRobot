#if UNITY_EDITOR
using System.IO;
using UnityEngine;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine.Rendering;
using System.Linq;
using UnityEditor.PackageManager;
using System.Collections.Generic;
using System.Diagnostics;
using UnityEditor.Callbacks;

namespace Unity.Simulation
{
    [InitializeOnLoad]
    class PreBuildStep: IPreprocessBuildWithReport
    {
        public int callbackOrder { get { return 0; } }

        private static string kPlayerResolutionAssetPath = "Assets/Resources/PlayerResolutionSettings.asset";

#pragma warning disable 414
        private static int maxElapsedTimeForImport = 60000;
#pragma warning restore 414

        private static GraphicsDeviceType[] _supportedGraphicsApis =
        {
            GraphicsDeviceType.OpenGLES2,
            GraphicsDeviceType.OpenGLES3,
            GraphicsDeviceType.OpenGLCore,
            GraphicsDeviceType.Vulkan
        };
        
        private static string[] _packagesToImport =
        {
#if UNITY_EDITOR_WIN
            "com.unity.toolchain.win-x86_64-linux-x86_64@0.1.18-preview",
#elif UNITY_EDITOR_OSX
            "com.unity.toolchain.macos-x86_64-linux-x86_64@0.1.19-preview",
#endif
        };


        [PostProcessBuild]
        public static void PostBuildCleanup(BuildTarget target, string pathToBuiltProject)
        {
            if (File.Exists(kPlayerResolutionAssetPath))
            {
                File.Delete(kPlayerResolutionAssetPath);
            }
        }

        static PreBuildStep()
        {
#if (UNITY_EDITOR_OSX || UNITY_EDITOR_WIN) && PLATFORM_CLOUD_RENDERING
            Log.I("Importing the toolchain packages");
            var timer = Stopwatch.StartNew();

            foreach (var package in _packagesToImport)
            {
                Log.I("Importing toolchain package: " + package);
                var req = UnityEditor.PackageManager.Client.Add(package);
                while (!req.IsCompleted)
                {
                    if (timer.ElapsedMilliseconds > maxElapsedTimeForImport)
                    {
                        timer.Stop();
                        Log.E("Failed to import the toolchain. Cannot crosscompile, quitting..");
                        EditorApplication.Exit(1);
                    }
                }

                Log.I("Done Importing toolchain packages.");
            }
            
            var definesString = PlayerSettings.GetScriptingDefineSymbolsForGroup(EditorUserBuildSettings.selectedBuildTargetGroup);
            var allDefines = definesString.Split ( ';' ).ToList();
            if (!allDefines.Contains("UNITY_STANDALONE_LINUX_API"))
                allDefines.Add("UNITY_STANDALONE_LINUX_API");
            
            PlayerSettings.SetScriptingDefineSymbolsForGroup (
                EditorUserBuildSettings.selectedBuildTargetGroup,
                string.Join (";", allDefines.ToArray()));
#endif
        }

        public void OnPreprocessBuild(BuildReport report)
        {
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
            CheckUSimRunCompatibility();
            BundlePlayerSettings();
        }

        private void BundlePlayerSettings()
        {
            if (Resources.Load<PlayerResolutionSettings>("PlayerResolutionSettings") == null)
            {
                var so = ScriptableObject.CreateInstance<PlayerResolutionSettings>();
                so.playerResolution = new PlayerResolution()
                {
                    height = PlayerSettings.defaultScreenHeight,
                    width = PlayerSettings.defaultScreenWidth
                };
                
                if (!Directory.Exists("Assets/Resources"))
                    Directory.CreateDirectory("Assets/Resources");
            
                AssetDatabase.CreateAsset(so, kPlayerResolutionAssetPath);
                AssetDatabase.SaveAssets();
            }
        }

        private void CheckUSimRunCompatibility()
        {
#if !PLATFORM_CLOUD_RENDERING
            if (EditorUserBuildSettings.activeBuildTarget != BuildTarget.StandaloneLinux64)
                Log.W("In order to run on Unity Simulation, you need to build a linux player");
            
            if (SystemInfo.graphicsDeviceType == GraphicsDeviceType.Vulkan)
                Log.W("In order to run with Vulkan in Unity Simulation, you need to build the player with CloudRendering Build target.");
            
            if (!_supportedGraphicsApis.Contains(SystemInfo.graphicsDeviceType))
                Log.W("The current GraphicsAPI is not supported in Unity Simulation.");
#endif
        }
    }
}
#endif