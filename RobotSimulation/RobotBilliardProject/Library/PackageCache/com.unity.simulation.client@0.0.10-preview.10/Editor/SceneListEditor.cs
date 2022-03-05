using System;
using System.Collections.Generic;

using UnityEngine;

using UnityEditor;
using UnityEditorInternal;

namespace Unity.Simulation.Client
{
    public class SceneListEditor
    {
        public List<SceneInfo> scenes = new List<SceneInfo>();
        public ReorderableList list;

        public SceneListEditor()
        {
            list = new ReorderableList(scenes, typeof(SceneInfo), false, true, true, true);
            list.drawHeaderCallback    += DrawHeaderCallback;
            list.drawElementCallback   += DrawElementCallback;
            list.elementHeightCallback += ElementHeightCallback;
        }

        public void OnGUI()
        {
            list.DoLayoutList();
        }

        void DrawHeaderCallback(Rect rect)
        {
            EditorGUI.LabelField(rect, "Select Scenes To Include");
        }

        void DrawElementCallback(Rect rect, int index, bool active, bool focused)
        {
            var element = scenes[index];

            element.hasError = element.scene == null || SceneAtIndexAlreadyAdded(index);

            var rc    = rect;
            rc.height = 20;
            rc.x     += 15;
            rc.width -= 15;
            rc.height = EditorGUIUtility.singleLineHeight;

            if (element.hasError)
            {
                EditorGUI.HelpBox(rc, "Scene asset cannot be null, or added multiple times.", MessageType.Error);
                rc.y += EditorGUIUtility.singleLineHeight + EditorGUIUtility.standardVerticalSpacing;
                rc.height = EditorGUIUtility.singleLineHeight;
            }

            element.scene = EditorGUI.ObjectField(rc, element.scene, typeof(SceneAsset), true) as SceneAsset;
        }

        float ElementHeightCallback(int index)
        {
            var length = scenes.Count;
            if (length <= 0)
                return 0;

            var element = scenes[index];

            var lines = 1 + (element.hasError ? 1 : 0);

            return lines * EditorGUIUtility.singleLineHeight + EditorGUIUtility.standardVerticalSpacing;
        }

        bool SceneAtIndexAlreadyAdded(int index)
        {
            if (index == 0)
                return false;
            var element = scenes[index];
            if (element.scene == null)
                return false;
            for (var i = 0; i < index; ++i)
                if (scenes[i].scene == element.scene)
                    return true;
            return false;
        }
    }
}

