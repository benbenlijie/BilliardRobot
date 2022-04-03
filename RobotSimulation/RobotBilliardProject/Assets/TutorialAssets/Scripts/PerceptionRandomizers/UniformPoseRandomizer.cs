using System.Collections;
using System.Collections.Generic;
using System;
using UnityEngine;
using UnityEngine.Perception.Randomization.Parameters;
using UnityEngine.Perception.Randomization.Randomizers;

[Serializable]
[AddRandomizerMenu("Perception/Uniform Pose Randomizer")]
public class UniformPoseRandomizer : Randomizer
{
    /*  Randomizes object's position and rotation relative to a fixed starting pose, over the specified range.
     *  
     *  Example use-case:
     *  Make very small random adjustments to the camera's pose, to make the learned model more robust
     *  to small inaccuracies in placing the real camera.
     */

    public float positionDistance = 0.5f;
    public Vector3 positionRanges = Vector3.zero;
    public float rotationRangeDegrees = 1.0f;

    public FloatParameter random; //(-1, 1)

    protected override void OnIterationStart()
    {
        IEnumerable<UniformPoseRandomizerTag> tags = tagManager.Query<UniformPoseRandomizerTag>();
        List<Vector3> positions_before = new List<Vector3>();
        foreach (UniformPoseRandomizerTag tag in tags)
        {
            bool isOk = false;
            while (!isOk)
            {
                Vector3 adjustedPosition = AdjustedVector(tag.rootPosePosition, positionRanges);
                isOk = true;
                foreach (var pos_before in positions_before)
                {
                    if (Vector3.SqrMagnitude(adjustedPosition - pos_before) < positionDistance)
                    {
                        isOk = false;
                        break;
                    }
                }
                if (isOk)
                {
                    positions_before.Add(adjustedPosition);
                    tag.gameObject.transform.position = adjustedPosition;
                }
            }
            
            Vector3 adjustedRotation = AdjustedVector(tag.rootPoseRotation, rotationRangeDegrees);
            tag.gameObject.transform.eulerAngles = adjustedRotation;
        }
    }

    // HELPERS

    private Vector3 AdjustedVector(Vector3 rootVector, Vector3 ranges)
    {
        float x = AdjustedValue(rootVector.x, ranges.x);
        float y = AdjustedValue(rootVector.y, ranges.y);
        float z = AdjustedValue(rootVector.z, ranges.z);
        Vector3 adjustedVector = new Vector3(x, y, z);
        return adjustedVector;
    }

    private Vector3 AdjustedVector(Vector3 rootVector, float range)
    {
        float x = AdjustedValue(rootVector.x, range);
        float y = AdjustedValue(rootVector.y, range);
        float z = AdjustedValue(rootVector.z, range);
        Vector3 adjustedVector = new Vector3(x, y, z);
        return adjustedVector;
    }

    private float AdjustedValue(float rootValue, float range)
    {
        float change = range * random.Sample();
        float adjustedVal = rootValue + change;
        return adjustedVal;
    }

}