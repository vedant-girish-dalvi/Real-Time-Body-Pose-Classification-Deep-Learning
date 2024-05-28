using System.Threading;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using uPLibrary.Networking.M2Mqtt;
using uPLibrary.Networking.M2Mqtt.Messages;
using uPLibrary.Networking.M2Mqtt.Utility;
using uPLibrary.Networking.M2Mqtt.Exceptions;
using System;
using System.Text.Json;
using System.Globalization;
using Newtonsoft.Json.Linq;

public class MQTTConnection : MonoBehaviour
{
    [Header("MQTT Configuration")]
    public string BrokerAddress = "broker.hivemq.com";
    public int BrokerPort = 1883;
    public string username = "";
    public string password = "";
    public string Topic_Angle = "mqtt-rokoko01-source";

    [Header("Mocap Data")]
    public ValueArmRight ScriptArmRight;
    public ValueArmLeft ScriptArmLeft;
    public ValueNeckHead ScriptHeadNeck;
    public ValuesLeg ScriptLeg;
    public ValueBack ScriptBack;

    private MqttClient client;
    private List<float[]> dataBuffer = new List<float[]>();
    private float nextActionTime = 0.0f;
    public float sampleInterval = 0.0166667f; // Interval for collecting samples (60 times per second)

    // Start is called before the first frame update
    void Start()
    {
        client = new MqttClient(BrokerAddress, BrokerPort, false, null);

        string clientId = Guid.NewGuid().ToString();
        client.Connect(clientId, username, password);
        client.Subscribe(new string[] { Topic_Angle }, new byte[] { MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE });
    }

    // Update is called once per frame
    void Update()
    {
        // Collect data every sampleInterval
        if (Time.time >= nextActionTime)
        {
            nextActionTime += sampleInterval;
            CollectData();
        }

        // Check if one second worth of data has been collected
        if (dataBuffer.Count >= 60)
        {
            PublishData();
            dataBuffer.Clear(); // Clear the buffer after publishing
        }
    }

    void CollectData()
    {
        float AngleElbowLeft = ScriptArmLeft.ELbowAngle;
        float AngleShoulderAbAdLeft = ScriptArmLeft.ShAdAbAngle;
        float AngleLowArmProSupLeft = ScriptArmLeft.lowArmPronateL;
        float AngleUpArmRotLeft = ScriptArmLeft.upArmRotateL;
        float AngleHandFlExLeft = ScriptArmLeft.handFlexL;
        float AngleHandRadDuctLeft = ScriptArmLeft.handRadDuctL;

        float AngleElbowRight = ScriptArmRight.ELbowAngle;
        float AngleShoulderAbAdRight = ScriptArmRight.ShAdAbAngle;
        float AngleShoulderFlExRight = ScriptArmRight.ShFlExAngle;
        float AngleLowArmProSupRight = ScriptArmRight.lowArmPronateR;
        float AngleUpArmRotRight = ScriptArmRight.upArmRotateR;
        float AngleHandFlExRight = ScriptArmRight.handFlexR;
        float AngleHandRadDuctRight = ScriptArmRight.handRadDuctR;

        float AngleNeckFlEx = ScriptHeadNeck.NeckFlExAngle;
        float AngleNeckTors = ScriptHeadNeck.NeckTors;
        float AngleHeadTilt = ScriptHeadNeck.HeadSideTilt;

        float AngleTorsoTilt = ScriptBack.BackFlex;
        float AngleTorsoSideTilt = ScriptBack.TorsoSideTilt;
        float AngleBackCurve = ScriptBack.BackCurve;
        float AngleBackTors = ScriptBack.BackTors;

        float AngleLegLeft = ScriptLeg.kneeLAngleStand;
        float AngleLegRight = ScriptLeg.kneeRAngleStand;

        float[] sample = {
            AngleNeckFlEx, AngleHeadTilt, AngleNeckTors,
            AngleElbowLeft, AngleElbowRight,
            AngleLegLeft, AngleLegRight,
            AngleTorsoTilt, AngleTorsoSideTilt
        };

        dataBuffer.Add(sample);
    }

    void PublishData()
    {
        // Convert data buffer to a JSON string
        string jsonData = Newtonsoft.Json.JsonConvert.SerializeObject(dataBuffer);
        // Publish the JSON data
        client.Publish(Topic_Angle, System.Text.Encoding.UTF8.GetBytes(jsonData), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, true);
        Debug.Log(jsonData); // Log the published data for debugging
        // client.Publish(Topic_Angle, System.Text.Encoding.UTF8.GetBytes(string.Join(",", dataBuffer)), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, true);
    }
}
