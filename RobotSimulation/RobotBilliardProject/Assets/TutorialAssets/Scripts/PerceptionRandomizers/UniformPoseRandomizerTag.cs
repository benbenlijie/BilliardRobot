using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Perception.Randomization.Randomizers;

[AddComponentMenu("Perception/RandomizerTags/UniformPoseRandomizerTag")]
public class UniformPoseRandomizerTag : RandomizerTag
{
    public Vector3 rootPosePosition;
    public Vector3 rootPoseRotation;

    public bool useOriginPos = false;

    private void Start()
    {
        if (useOriginPos)
        {
            rootPosePosition = transform.position;
            rootPoseRotation = transform.eulerAngles;
        }
    }

}