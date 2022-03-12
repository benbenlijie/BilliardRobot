using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CueStick : MonoBehaviour
{
    public float forceAmount = 1.0f;
    public bool hitObject = true;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnTriggerEnter(Collider other)
    {
        if (hitObject == false)
        {
            var rigid = other.GetComponent<Rigidbody>();
            var force = transform.rotation * new Vector3(0, 0, forceAmount);
            rigid.AddForce(force, ForceMode.Impulse);
            hitObject = true;
        }
    }
}
