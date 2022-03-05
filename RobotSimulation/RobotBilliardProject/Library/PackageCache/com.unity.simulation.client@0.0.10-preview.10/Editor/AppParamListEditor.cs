using System;
using System.IO;
using System.Collections.Generic;

using UnityEngine;

using UnityEditor;
using UnityEditorInternal;

namespace Unity.Simulation.Client
{
    public class AppParamListEditor
    {
        public List<AppParamInfo> appParams = new List<AppParamInfo>();
        public ReorderableList    list;

        public AppParamListEditor()
        {
            list = new ReorderableList(appParams, typeof(AppParamInfo), false, true, true, true);
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
            EditorGUI.LabelField(rect, "Select Application Parameters");
        }

        void DrawElementCallback(Rect rect, int index, bool active, bool focused)
        {
            var element = appParams[index];

            element.hasError = element.appParam == null || string.IsNullOrEmpty(element.name) || element.instanceCount == 0 || NameAtIndexAlreadyUsed(index);

            var rc    = rect;
            rc.height = 20;
            rc.x     += 15;
            rc.width -= 15;

#if UNITY_2019_3_OR_NEWER
            element.isExpanded = EditorGUI.BeginFoldoutHeaderGroup(rc, element.isExpanded, element.name);
#endif
            if (element.isExpanded)
            {
                EditorGUI.indentLevel++;

                if (string.IsNullOrEmpty(element.name) || NameAtIndexAlreadyUsed(index))
                {
                    rc.y     += EditorGUIUtility.singleLineHeight + EditorGUIUtility.standardVerticalSpacing;
                    rc.height = EditorGUIUtility.singleLineHeight;
                    EditorGUI.HelpBox(rc, "App parameter name must not be empty or used previously.", MessageType.Error);
                }

                rc.y                 += EditorGUIUtility.singleLineHeight + EditorGUIUtility.standardVerticalSpacing;
                rc.height             = EditorGUIUtility.singleLineHeight;
                element.name          = EditorGUI.TextField(rc, "Name", element.name);

                if (element.instanceCount == 0)
                {
                    rc.y += EditorGUIUtility.singleLineHeight + EditorGUIUtility.standardVerticalSpacing;
                    rc.height = EditorGUIUtility.singleLineHeight;
                    EditorGUI.HelpBox(rc, "App parameter instances must be greater than 0.", MessageType.Error);
                }

                rc.y                 += rc.height + EditorGUIUtility.standardVerticalSpacing;
                rc.height             = EditorGUIUtility.singleLineHeight;
                element.instanceCount = EditorGUI.IntField(rc, "Instances", element.instanceCount);

                var lastAppParam = element.appParam;

                if (element.appParam == null)
                {
                    rc.y += EditorGUIUtility.singleLineHeight + EditorGUIUtility.standardVerticalSpacing;
                    rc.height = EditorGUIUtility.singleLineHeight;
                    EditorGUI.HelpBox(rc, "App parameter must be assigned a ScriptableObject", MessageType.Error);
                }

                rc.y                 += rc.height + EditorGUIUtility.standardVerticalSpacing;
                rc.height             = EditorGUIUtility.singleLineHeight;
                element.appParam      = EditorGUI.ObjectField(rc, "ScriptableObject", element.appParam, typeof(ScriptableObject), false) as ScriptableObject;

                if (element.appParam != lastAppParam)
                {
                    if (element.appParam != null)
                    {
                        if (element.instanceCount == 0)
                            element.instanceCount = 1;

                        element.json = JsonUtility.ToJson(element.appParam, true).Trim();
                        element.jsonLineCount = element.json.Split('\n').Length;
                    }
                    else
                    {
                        element.name = "";
                        element.instanceCount = 0;
                    }
                }

                if (element.appParam != null)
                {
                    rc.y += rc.height + EditorGUIUtility.standardVerticalSpacing;
                    element.expandJson = EditorGUI.Foldout(rc, element.expandJson, "JSON");
                    if (element.expandJson)
                    {
                        rc.y += rc.height + EditorGUIUtility.standardVerticalSpacing;
                        rc.height = element.jsonLineCount * EditorGUIUtility.singleLineHeight;
                        EditorGUI.TextArea(rc, element.json);
                    }
                }

                EditorGUI.indentLevel--;
            }
#if UNITY_2019_3_OR_NEWER
            EditorGUI.EndFoldoutHeaderGroup();
#endif
        }

        float ElementHeightCallback(int index)
        {
            if (appParams.Count <= 0)
                return 0;

            var element = appParams[index];

            float height = EditorGUIUtility.singleLineHeight + EditorGUIUtility.standardVerticalSpacing;

            if (!element.isExpanded)
                return height;

            var lineCount = 4; // This is the number of public fields in AppParamInfo + the Foldout. 

            if (string.IsNullOrEmpty(element.name) || NameAtIndexAlreadyUsed(index))
                ++lineCount;

            if (element.instanceCount == 0)
                ++lineCount;

            if (element.appParam == null)
                ++lineCount;

            if (element.json != null)
            {
                if (element.expandJson)
                    lineCount += element.jsonLineCount;
            }

            height += lineCount * (EditorGUIUtility.singleLineHeight + EditorGUIUtility.standardVerticalSpacing);

            return height;
        }

        bool NameAtIndexAlreadyUsed(int index)
        {
            if (index == 0)
                return false;
            var element = appParams[index];
            if (string.IsNullOrEmpty(element.name))
                return false;
            for (var i = 0; i < index; ++i)
                if (!string.IsNullOrEmpty(appParams[i].name) && appParams[i].name.Equals(element.name))
                    return true;
            return false;
        }
    }
}

