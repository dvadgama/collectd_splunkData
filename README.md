# collectd_splunkData
A collectd Python Plugin for SplunkData 

####Why?
While curl_json/curl_xml plugin works to get the 90% of the information via REST API end points suchs as 

- server/introspection/indexer
- status/resource-usage/splunk-processes
- server/status/resource-usage/hostwide

 There are certain end points which holds the useful information and, return it back to you as CDATA  JSON string. example of such a endpoint is 

- introspection/kvstore/serverstatus

 and , JSON out put looks like this
<code>
<pre>
{
"links":
    {
    },
    "origin": "https://localhost/services/server/introspection/kvstore/serverstatus",
    "generator":
    {
        "build": "1",
        "version": "x.y.z"
    },
    "entry":
    [
        {
            "name": "serverStatus",
             "data": <Font style="BACKGROUND-COLOR: black"> {"host": "localhost","connections": { "available":10 , "current":2,"toalCreated":3  }" </Font>,
             .....
             .....
	}
   ],
 . . .
 . . .
}
</pre>
</code>

observer the highlighted area, it not a JSON but CDATA , i.e. json embaded as a value of field/key data and, curl_json,curl_xml will not be able to process it because it is a <b>*VALUE* </b> and , those plugins can only display it. As they are suppose to.

Hence, We need another plugin which can extract these information from these CDATA ( by converting it into JSON :) )

#### Leaf Key/Parameters
- Host: host name of your splunk api server ( Note that API server  is not same as the web front end of splunk )
- Port : port on which splunk responses
- userName: your splunk login
- userPasswor: your splunk password
- URL:  API endpoint ,  <b>do not forget to add  <i> output_mode=json </i> at the end. Yes, this plugin can not handle the xml data</b>
- Type: specify one of the collectd data type, as found in types.db

#### node Key/Paramters
- Path: it is a Forward-slash ( i.e. '/' ) seperated path to where your value of interest lies

i.e. refering to above example , if i want to know availabe connections , i would use 

<code>
<pre>< Path "connections/available" >
      Type "gauge"
< /Path ></pre>
</code>

#### Notes
- place the python module in a directory say /my/collectd/plugins/python before using it.
- Refer to the splunk.conf for splunkData configuration and [collectd python]('https://collectd.org/documentation/manpages/collectd-python.5.shtml') for Python Plguin configuration in general
- I used [redis-collectd-plugin]('https://github.com/powdahound/redis-collectd-plugin') as refrence while developing this plugin


