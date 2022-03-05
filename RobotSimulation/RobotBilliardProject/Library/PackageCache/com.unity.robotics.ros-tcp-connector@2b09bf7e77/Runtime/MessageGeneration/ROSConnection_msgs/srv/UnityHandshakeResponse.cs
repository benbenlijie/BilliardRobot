//Do not edit! This file was generated by Unity-ROS MessageGeneration.
using System;
using System.Linq;
using System.Collections.Generic;
using System.Text;
using Unity.Robotics.ROSTCPConnector.MessageGeneration;

namespace RosMessageTypes.RosTcpEndpoint
{
    public class UnityHandshakeResponse : Message
    {
        public const string RosMessageName = "ros_tcp_endpoint/UnityHandshake";

        public string ip;

        public UnityHandshakeResponse()
        {
            this.ip = "";
        }

        public UnityHandshakeResponse(string ip)
        {
            this.ip = ip;
        }
        public override List<byte[]> SerializationStatements()
        {
            var listOfSerializations = new List<byte[]>();
            listOfSerializations.Add(SerializeString(this.ip));

            return listOfSerializations;
        }

        public override int Deserialize(byte[] data, int offset)
        {
            var ipStringBytesLength = DeserializeLength(data, offset);
            offset += 4;
            this.ip = DeserializeString(data, offset, ipStringBytesLength);
            offset += ipStringBytesLength;

            return offset;
        }

        public override string ToString()
        {
            return "UnityHandshakeResponse: " +
            "\nip: " + ip.ToString();
        }
    }
}
