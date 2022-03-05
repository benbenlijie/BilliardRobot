using System;
using System.Diagnostics;
using System.Collections;
using System.Collections.Generic;
using System.IO;

using NUnit.Framework;
using UnityEngine;
using UnityEditor;
using UnityEngine.TestTools;

using Unity.Simulation;
using Unity.Simulation.Client;

using Debug = UnityEngine.Debug;

namespace Unity.Simulation.Client.Tests
{
    // All of the tests below require a logged in user to auth with usim backend.
    // For now, disabling these tests, and providing a fake test to satisfy validation.

    public class FakeTest
    {
        [Test]
        public void FakeTest_Succeeds()
        {}
    }

#if UNITY_2019_3_OR_NEWER
#if UNITY_EDITOR && UNITY_SIMULATION_ENABLE_CLIENT_TESTS

    public static class TestUtility
    {
        public static bool IsAutomatedTestRun()
        {
            return Array.IndexOf(Environment.GetCommandLineArgs(), "-runTests") >= 0;
        }
    }

    public struct TestAppParam
    {
        public int value;
        public TestAppParam(int value)
        {
            this.value = value;
        }
    }

    public class ClientTests
    {
#if UNITY_SIMULATION_ENABLE_BUILD_TEST_PROJECT
        [MenuItem("Simulation/Tests/Build Test Project")]
        // Need to figure out a way to build the test project before the tests run without polluting the menu bar.
        static void BuildTestProject()
        {
            if (File.Exists(zipPath))
                File.Delete(zipPath);
            Assert.False(File.Exists(zipPath));
            var scenes = new string[]
            {
                "Packages/com.unity.simulation.client/Tests/TestScene.unity",
            };
            Project.BuildProject(Path.Combine(buildPath, projectName), projectName, scenes);
            Assert.True(File.Exists(zipPath));
        }
#endif

        public static string projectName
        {
            get { return "TestBuild"; }
        }

        public static string projectPath
        {
            get { return Directory.GetParent(Application.dataPath).FullName; }
        }

        public static string buildPath
        {
            get { return Path.Combine(projectPath, "Build"); }
        }
        public static string zipPath
        {
            get { return Path.Combine(buildPath, projectName + ".zip"); }
        }

        Run run = null;

        [OneTimeSetUp]
        public void Setup()
        {
            if (File.Exists(zipPath))
            {
                run = Run.Create("test", "test run");
                var sysParam = API.GetSysParams()[0];
                run.SetSysParam(sysParam);
                run.SetBuildLocation(zipPath);
                run.SetAppParam("test", new TestAppParam(1), 1);
                run.Execute();
            }
        }

        public IEnumerator WaitForRunToComplete()
        {
            Assert.True(run != null);

            var stopwatch = new Stopwatch();
            stopwatch.Start();

            var timeoutSecs = 600;
            while (stopwatch.Elapsed.TotalSeconds < timeoutSecs && !run.completed)
                yield return null;

            Debug.Log($"Run State code: {run.summary.state.code} source: {run.summary.state.source}");

            Assert.True(run.completed);
            Assert.True(run.summary.num_success     == 1);
            Assert.True(run.summary.num_failures    == 0);
            Assert.True(run.summary.num_in_progress == 0);
            Assert.True(run.summary.num_not_run     == 0);
        }

        [Test]
        public void ClientTests_GetSysParamSucceeds()
        {
            var sysParams = API.GetSysParams();
            Assert.True(sysParams.Length != 0);
        }

        [UnityTest]
        public IEnumerator ClientTests_ExecutedRunCompletes()
        {
            yield return WaitForRunToComplete();
            Assert.True(run.summary.num_success == 1);
        }

        [UnityTest]
        public IEnumerator ClientTests_TestSummarize()
        {
            yield return WaitForRunToComplete();
            var summary = API.Summarize(run.executionId);
            Assert.True(summary.num_success == 1);
        }

        [UnityTest]
        public IEnumerator ClientTests_TestDescribe()
        {
            yield return WaitForRunToComplete();
            var description = API.Describe(run.executionId);
        }

        [UnityTest]
        public IEnumerator ClientTests_TestGetManifest()
        {
            yield return WaitForRunToComplete();
            var manifest = API.GetManifest(run.executionId);
            Assert.True(manifest.Count > 1);
        }

        [UnityTest]
        [Timeout(1000000000)]
        public IEnumerator ClientTests_UploadLargeBuildAsync()
        {
            var fileSize = 500 * 1024 * 1024;
            var path = Path.Combine(Application.persistentDataPath, "DeleteTestFile.bin");

            if (!File.Exists(path))
            {
                FileStream fs = new FileStream(path, FileMode.CreateNew);
                fs.Seek(fileSize, SeekOrigin.Begin);
                fs.WriteByte(0);
                fs.Close();
            }

            var task = API.UploadBuildAsync("ClientTests", path, progress: progress =>
            {
                if (EditorUtility.DisplayCancelableProgressBar(
                    $"Upload {path}",
                    "Shows a progress bar for the upload build progress",
                    progress))
                {
                    EditorUtility.ClearProgressBar();
                    Debug.Log("Progress bar canceled by the user");
                }
            })
            .ContinueWith(uploadTask =>
            {
                EditorUtility.ClearProgressBar();
                Debug.Log($"UploadComplete: build id => {uploadTask.Result}");
            });

            while (!task.IsCompleted)
                yield return null;
        }

        [Test]
        public void ClientTests_TestBatchAppParamUpload()
        {
            var d = new Dictionary<string, object>();
            for (var i = 0; i < 100; ++i)
                d[$"app-param-{i}"] = new TestAppParam(i);

            var result = API.UploadAppParamBatch(d);

            Assert.NotNull(result);

            foreach (var kv in result)
                Debug.Log($"app-param: {kv.Key} => {kv.Value}");

            Assert.True(result.Count == d.Count);
        }
    }

#endif // UNITY_EDITOR
#endif // UNITY_2019_3_OR_NEWER

}
