#if UNITY_EDITOR
using System.IO;

using UnityEngine;

namespace Unity.Simulation.Client
{
    public abstract class TestBuild<T> where T : TestBuild<T>, new()
    {
        public struct TestAppParam
        {
            public int TestField;
        }

        static T _instance;
        public static T Instance
        {
            get
            {
                if (_instance == null)
                    _instance = new T();
                return _instance;
            }
        }

        // Derived classes just implement projectName
        public abstract string projectName
        {
            get;
        }

        public string buildPath
        {
            get { return Path.Combine(Application.dataPath, "..", "Build"); }
        }

        public string projectPath
        {
            get { return Path.Combine(buildPath, projectName); }
        }

        public string zipPath
        {
            get { return Path.Combine(buildPath, projectName + ".zip"); }
        }
    }
}
#endif // UNITY_EDITOR
