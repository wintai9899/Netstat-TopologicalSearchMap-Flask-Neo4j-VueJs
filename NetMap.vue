<template>
    
    <Row style="margin-top:5px">
        <Col span="4" >
          <div style="margin-left-5px;background-image: linear-gradient(to bottom , #384861 ,#399379)">
            <header style="font-size:45px;font-weight:bolder;margin-left:5px;color:#3DB983;font-family:Airstrike;text-stroke:0.2px #ffffff">NETSTAT MAP</header>
            <span style="margin-top:10px;font-size:15px;font-weight:bolder;margin-left:5px;color:#eaf4fc;font-family:Georgia">快速查询</span><br>
            <!-- 快速查询按钮 -->
            <div class="link-top"></div><br>
            <Button v-if="query.show_all_hosts" type="primary" shape="circle" style="margin-right:20px;color:#ffffff" @click="get_All_Host_Data()">主机</Button>
            <Button v-if="query.show_all_ip" type="primary" shape="circle" style="margin-right:20px;color:#ffffff" @click="get_All_Ip_Data()">IP</Button>
            <Button v-if="query.show_internal_ip" type="primary" shape="circle" style="margin-right:20px;color:#ffffff" @click="get_internal_ip()">内网IP</Button><br>
            <br>
            <Button v-if="query.show_external_ip" type="primary" shape="circle" style="margin-right:20px;color:#ffffff" @click="get_external_ip()">外网IP</Button>
            <Button v-if="query.show_80" type="primary"  shape="circle" style="margin-right:15px;color:#ffffff" @click="get_80()">80端口</Button><br>
            <br>
            <Button v-if="query.internal_to_external" type="primary"  shape="circle" style="margin-right:15px;color:#ffffff" @click="get_internal_to_external()">内网与外网IP连接</Button>
            
            <!-- <br>
            <br>
            <Select id = 'select_limit' v-model="query.node_limit" size="small" style="width:100px" ><br>
            <br>
                <Option value="50">50个节点</Option>
                <Option value="100">100个节点</Option>
                <Option value="200">200个节点</Option>
                <Option value="300">300个节点</Option>
                <Option value="500">500个节点</Option>
            </Select> -->
            <br>
            <br>
            <span style="margin-top:10px;font-size:15px;font-weight:bolder;margin-left:5px;color:#eaf4fc;font-family:Georgia;">连接状态</span><br>
            <div class="link-top"></div><br>
            <Button v-if="query.show_estab" type="primary" style="margin-right:15px;;color:#ffffff" @click="get_estab()">ESTAB</Button>
            <Button v-if="query.show_listen" type="primary" style="margin-right:15px;color:#ffffff" @click="get_listen()">LISTEN</Button>
            <Button v-if="query.show_request" type="primary" style="margin-right:15px;color:#ffffff" @click="get_request()">REQUEST</Button>
            <br>
            <br>
            <Button v-if="query.show_unconn" type="primary" style="margin-right:15px;color:#ffffff" @click="get_unconn()">UNCONN</Button>
            <br>
            <br>
            <div class="link-top"></div><br>
            <Button id='downloadImage' icon="ios-download-outline" style="background-color:#95a2a3;color:#eaf4fc" @click="graph.downloadFullImage()" >点击保存图片</Button>
            <br>
            <br>

            <!--                 查询方法选择器                -->
            <span style="margin-top:10px;font-size:15px;font-weight:bolder;margin-left:5px;color:#eaf4fc;font-family:Georgia">请选择服务</span><br>
            <Select id = 'selectBox' v-model="query.type" style="width:200px; " onchange='changeFunc(value);'>
              
                <Option value="node">HOST/IP节点查询</Option>
                <Option value="path">IP路径查询</Option>
                <Option value="host_path">HOST路径查询</Option>
                <Option value="network_segment">网段查询</Option>
                <Option value="upload">上传数据</Option>
                <Option value="log_in">登陆青藤云</Option>
              
            </Select>
            <br>
            <br>
            <!-- <Button type="primary" @click="getNetMapData()" style="margin-left:5px;width:100px;margin-bottom:25px;margin-top:25px">查询</Button> -->
            <!--                 查询表单                -->
            <Form ref="query" v-model="query" inline>
              <div v-show="query.type=='node'">
              <span style="font-family:Georgia;margin-left:70px;font-weight:bolder;color:#eaf4fc;font-size:25px;">查询主机</span>
              <FormItem prop="single_host">
                <Input type="text" v-model="query.single_host" style="margin-top:10px;" placeholder="请输入主机名称">
                <Icon type="ios-desktop" slot="prepend"></Icon>
                </Input>
              </FormItem>
              <span style="margin-left:85px;font-weight:bolder;color:#eaf4fc;font-size:25px;font-family:Georgia;">查询IP</span>
              <FormItem prop="single_ip">
                <Input type="text" v-model="query.single_ip" placeholder="请输入IP地址" style="margin-top:10px;">
                <Icon type="ios-navigate" slot="prepend"></Icon>
                </Input>
                <RadioGroup v-model="query.ip_node">
                  <Radio label="ip_connect" style="color:#eaf4fc"><span>显示关联IP</span></Radio >
                  <Radio label="open_port" style="color:#eaf4fc"><span>显示开放端口</span></Radio >
                </RadioGroup>
              </FormItem>
                <span style="margin-left:70px;font-weight:bolder;color:#eaf4fc;font-size:25px;font-family:Georgia;">查询端口</span>
              <FormItem prop="single_port">
                <Input type="text" v-model="query.single_port" placeholder="请输入端口号" style="margin-top:10px;">
                <Icon type="ios-keypad" slot='prepend'></Icon>
                </Input>
              </FormItem>
              <Button type="primary" long @click="getNetMapData()" icon="ios-search" style="color:#eaf4fc">查询</Button>
              </div>

              <div v-show="query.type=='network_segment'">
              <span style="font-family:Georgia;margin-left:70px;font-weight:bolder;color:#eaf4fc;font-size:25px;">查询网段</span>
              <FormItem prop="segment">
                <Input type="text" v-model="query.segment" style="margin-top:10px;" placeholder="请输入网段">
                <Icon type="ios-desktop" slot="prepend"></Icon>
                </Input>
              </FormItem>
                <RadioGroup v-model="query.segment_filter">
                  <Radio label="show_segment_host" style="color:#eaf4fc"><span>显示该网段所有主机</span></Radio >
                  <Radio label="show_segment_ip" style="color:#eaf4fc"><span>显示该网段所有IP</span></Radio >
                </RadioGroup>

              <Button type="primary" long @click="getNetMapData()" icon="ios-search" style="color:#eaf4fc">查询</Button>
              </div>

              <div v-show="query.type=='path'">
                <span style="margin-left:20px;font-weight:bolder;color:#eaf4fc;font-size:25px;font-family:Georgia">查询两个IP之间的路径</span>
              <FormItem prop="from">
                <Input type="text" v-model="query.from" placeholder="请输入源IP地址" style="margin-top:10px;">
                <Icon type="ios-navigate" slot="prepend"></Icon>
                </Input>
                <span>
                  <Icon type="md-arrow-down" style="margin-left:90px"></Icon>
                </span>
              </FormItem>
              <FormItem prop="to">
              <Input type="text" v-model="query.to" placeholder="请输入目的IP地址（可选）" style="margin-top:-30px;">
              <Icon type="ios-navigate" slot="prepend" ></Icon>
              </Input>
              </FormItem><br>
              <!--                 路径显示单选框               -->
                <RadioGroup v-model="query.path">
                  <Radio style='color:#eaf4fc' label="short"><span>最短路径</span></Radio >
                  <Radio style='color:#eaf4fc' label="all"><span>全部路径</span></Radio >
                  <Radio style='color:#eaf4fc' label="ip_only"><span>仅显示关联IP</span></Radio >
                </RadioGroup>
                <!--                 设置特定查询条件               -->
                <FormItem prop="port">
                <br>
                <span style="margin-left:20px;font-weight:bolder;font-size:18px;color:#eaf4fc;font-size:25px;font-family:Georgia">设置查询路径条件(可选)</span><br>
                <span style="font-weight:bolder;color:#eaf4fc">IP之间必经过某个端口</span>
                <Input type="text" v-model="query.port" placeholder="端口号" style="width:50%" > 
                <Icon type="ios-keypad" slot='prepend'></Icon>
                </Input>
              </FormItem>
              <FormItem prop="protocol">
                <span style="font-weight:bolder;color:#eaf4fc;font-family:Georgia">传输协议(TCP/UDP 等等)</span>
                <Input type="text" v-model="query.protocol" placeholder="协议" style="width:50%"> 
                  <Icon type="ios-call" slot="prepend"></Icon>
                </Input>
              </FormItem>
              <FormItem prop="process">
                <span style="color:font-weight:bolder;color:#a2caff;font-family:Georgia">路径中必须经过拥有此服务的端口</span>
                <Input type="text" v-model="query.process" placeholder="端口服务" style="width:50%"> 
                  <Icon type="ios-globe" slot='prepend'></Icon>
                </Input>
              </FormItem>
              <Button type="primary" long @click="getNetMapData()" icon="ios-search" style="color:#eaf4fc;fill:red">查询</Button>
              </div>

              <div v-show="query.type=='host_path'">
                <span style="margin-left:20px;font-weight:bolder;color:#a2caff;font-size:20px;font-family:Georgia">查询两个HOST之间的路径</span>
              <FormItem prop="host_from">
                <Input type="text" v-model="query.host_from" placeholder="请输入源HOST名称" style="margin-top:10px;">
                <Icon type="ios-desktop" slot="prepend"></Icon>
                </Input>
                
                <span>
                  <Icon type="md-arrow-down" style="margin-left:90px"></Icon>
                </span>
              </FormItem>
              <FormItem prop="host_to">
              <Input type="text" v-model="query.host_to" placeholder="请输入目的HOST名称" style="margin-top:-30px;">
              <Icon type="ios-desktop" slot="prepend" ></Icon>
              </Input>
              </FormItem>
              <RadioGroup v-model="query.host_path_filter">
                  <Radio label="short_host" style="color:#eaf4fc"><span>最短路径</span></Radio >
                  <Radio label="all_host" style="color:#eaf4fc"><span>全部路径</span></Radio >
              </RadioGroup>
              <FormItem prop="host_to_id">
              <Input type="text" v-model="query.host_to_id" placeholder="请输入源HOST ID(可选)" style="margin-top:15px;">
              <Icon type="ios-desktop" slot="prepend" ></Icon>
              </Input>
              </FormItem>
              <FormItem prop="host_to_id">
              <Input type="text" v-model="query.host_from_id" placeholder="请输入目的HOST ID(可选)">
              <Icon type="ios-desktop" slot="prepend" ></Icon>
              </Input>
              </FormItem>
              <Button type="primary" long @click="getNetMapData()" icon="ios-search" style="color:#eaf4fc">查询</Button>
              </div>
              
            </Form>
            <div v-show="query.type=='upload'">
            <span style="font-size:25px;font-weight:bolder;color:#eaf4fc;font-family:Georgia">上传数据</span>
            <br>
            <br>
            <Select id = 'selectBox2' v-model="query.file_type" style="width:200px; " onchange='changeFunc(value);'>
              <Option value="qty_data">青藤云数据</Option>
              <Option value="netstat_data">NETSTAT数据</Option>
            </Select><span>请选择数据源</span>
              <div v-show="query.file_type=='qty_data'">
                <br>
                <Upload action="http://127.0.0.1:5000/uploadqty">
                  <Button icon="ios-cloud-upload-outline">Upload files</Button>
                </Upload>
                <br>
                <br>
                <br>
                <br>
              </div>
              <div v-show="query.file_type=='netstat_data'">
                <br>
                <Upload action="http://127.0.0.1:5000/uploadnetstat">
                    <Button icon="ios-cloud-upload-outline">Upload files</Button>
                </Upload>
                <br>
                <br>
              </div>
            </div>
            <div v-show="query.type=='log_in'">
            <span style="font-size:25px;font-weight:bolder;color:#eaf4fc;font-family:Georgia">登陆青藤云</span>
            <Form ref="formInline" :model="formInline" :rules="ruleInline" inline>
                <FormItem prop="user">
                    <Input type="text" v-model="formInline.user" placeholder="Username">
                        <Icon type="ios-person-outline" slot="prepend"></Icon>
                    </Input>
                </FormItem>
                <FormItem prop="password">
                    <Input type="password" v-model="formInline.password" placeholder="Password">
                        <Icon type="ios-lock-outline" slot="prepend"></Icon>
                    </Input>
                </FormItem>
                <FormItem>
                    <Button type="primary" @click="handleSubmit('formInline')">Signin</Button>
                </FormItem>
            </Form>
            </div>
            <!-- <div class="minimap"></div> -->
            </div>
            
        </Col>
        <Col span="20">
            <div  ref="imageTofile" id='cy' style="position: relative; border-left: 1px solid #9b9b9b;">
              <Spin fix v-if="loading">
                <Icon type="ios-loading" size=18 style="animation: ani-demo-spin 1s linear infinite;"></Icon>
                <div>Loading</div>
              </Spin>
            
            </div>
        </Col>
    </Row>

</div>
</template>

<script>
import G6, { Minimap } from '@antv/g6';
import axios from "axios";
import MiniMap from '@antv/g6/lib/plugins/minimap';
import Grid from '@antv/g6/lib/plugins/grid';
import ToolBar from '@antv/g6/lib/plugins/toolBar';
import Chart from 'chart.js';
import html2canvas from "html2canvas";


export default {
  name: "NetMap",
  components: {},
  data() {
    return {

        query:{
            type:"node",
            single_host:null,
            single_ip:null,
            single_port:null,
            from: null,
            to:null,
            port: null,
            process: null,
            protocol: null,
            path: "all",
            status:"status",

            host_path:"host_path",
            host_from:null,
            host_to:null,
            host_path_filter:'all',
            host_to_id :null,
            host_from_id:null,
            ip_node:'ip_node',

            network_segment:"network_segment",
            segment:null,
            segment_filter:'all',

            show_all_hosts:'show_all_hosts',
            show_all_ip:'show_all_ip',
            show_internal_ip:'show_internal_ip',
            show_external_ip:'show_external_ip',
            show_80:"show_80",

            show_estab:'show_estab',
            show_listen:'show_listen',
            show_request:'show_request',
            show_unconn:'show_unconn',
            show_close:'show_close',
            show_syn_sent:'show_syn_sent',
            internal_to_external:'internal_to_external',

            node_limit:'node_limit'
            
        },       
      
      g6: {
        edges: [],
        nodes: []
      },
      loading: false,
      graph: null,
      
      formInline: {
                    user: '',
                    password: ''
                },
                ruleInline: {
                    user: [
                        { required: true, message: 'Please fill in the user name', trigger: 'blur' }
                    ],
                    password: [
                        { required: true, message: 'Please fill in the password.', trigger: 'blur' },
                        { type: 'string', min: 6, message: 'The password length cannot be less than 6 bits', trigger: 'blur' }
                    ]
                },
                
    };
  },
  methods: {
    handleSubmit(name) {
      this.$refs[name].validate((valid) => {
      if (valid) {
        this.$Message.success('Success!');
      } else {
        this.$Message.error('Fail!');
      }
    })
    },

    handleAdd () {
        this.index++;
        this.query.items.push({
            value: '',
            index: this.index,
            status: 1
        });
    },

    getNetMapData() {
      let self = this;
      let params = {
        single_host:this.query.single_host,
        single_ip:this.query.single_ip,
        single_port:this.query.single_port,
        from: this.query.from, 
        to: this.query.to,
        port:this.query.port,
        protocol:this.query.protocol,
        process:this.query.process,
        ip_to_ip:this.query.ip_to_ip,
        host_from:this.query.host_from,
        host_to:this.query.host_to,
        path:this.query.path,
        node:this.query.path,
        host_path:this.query.host_path,
        type : this.query.type,
        host_path_filter: this.query.host_path_filter,
        host_to_id: this.query.host_to_id,
        host_from_id:this.query.host_from_id,
        ip_node:this.query.ip_node,
        
        network_segment:this.query.network_segment,
        segment:this.query.segment,
        segment_filter:this.query.segment_filter

        }

        self.loading = true
        axios.get("http://localhost:5000/json", {params: params}).then(function(response) {
        let data = response.data;
        self.g6 = data.elements // 修改，格式匹配
        self.loading = false
        self.render();
        
      });
    },
    get_All_Host_Data() {
      let self = this;
      let params = {
        show_all_hosts : this.query.show_all_hosts,
        node_limit:this.query.node_limit
        
        }
        self.loading = true
        axios.get("http://localhost:5000/show_all_node", {params: params}).then(function(response) {
        let data = response.data;
        self.g6 = data.elements // 修改，格式匹配
        self.loading = false
        self.render();
        
      });
    },

    get_All_Ip_Data() {
      let self = this;
      let params = {
        show_all_ip : this.query.show_all_ip,
        }
        self.loading = true
        axios.get("http://localhost:5000/show_all_node", {params: params}).then(function(response) {
        let data = response.data;
        self.g6 = data.elements // 修改，格式匹配
        self.loading = false
        self.render();
        
      });
    },

    get_internal_ip() {
      let self = this;
      let params = {
        show_internal_ip : this.query.show_internal_ip
        }
        self.loading = true
        axios.get("http://localhost:5000/show_all_node", {params: params}).then(function(response) {
        let data = response.data;
        self.g6 = data.elements // 修改，格式匹配
        self.loading = false
        self.render();
        
      });
    },

    get_external_ip() {
      let self = this;
      let params = {
        show_external_ip : this.query.show_external_ip,
        }
        self.loading = true
        axios.get("http://localhost:5000/show_all_node", {params: params}).then(function(response) {
        let data = response.data;
        self.g6 = data.elements // 修改，格式匹配
        self.loading = false
        self.render();
        
      });
    },

    get_estab(){
      let self = this;
      let params = {
        show_estab : this.query.show_estab
        }
        self.loading = true
        axios.get("http://localhost:5000/show_all_node", {params: params}).then(function(response) {
        let data = response.data;
        self.g6 = data.elements // 修改，格式匹配
        self.loading = false
        self.render();
        
      });
    },

    get_listen(){
      let self = this;
      let params = {
        show_listen : this.query.show_listen
        }
        self.loading = true
        axios.get("http://localhost:5000/show_all_node", {params: params}).then(function(response) {
        let data = response.data;
        self.g6 = data.elements // 修改，格式匹配
        self.loading = false
        self.render();
        
      });
    },

    get_request(){
      let self = this;
      let params = {
        show_request : this.query.show_request
        }
        self.loading = true
        axios.get("http://localhost:5000/show_all_node", {params: params}).then(function(response) {
        let data = response.data;
        self.g6 = data.elements // 修改，格式匹配
        self.loading = false
        self.render();
        
      });
    },

    get_unconn(){
      let self = this;
      let params = {
        show_unconn : this.query.show_unconn
        }
        self.loading = true
        axios.get("http://localhost:5000/show_all_node", {params: params}).then(function(response) {
        let data = response.data;
        self.g6 = data.elements // 修改，格式匹配
        self.loading = false
        self.render();
        
      });
    },
    get_80(){
      let self = this;
      let params = {
        show_80 : this.query.show_80
        }
        self.loading = true
        axios.get("http://localhost:5000/show_all_node", {params: params}).then(function(response) {
        let data = response.data;
        self.g6 = data.elements // 修改，格式匹配
        self.loading = false
        self.render();
        
      });
    },
    get_internal_to_external(){
      let self = this;
      let params = {
        internal_to_external : this.query.internal_to_external
        }
        self.loading = true
        axios.get("http://localhost:5000/show_all_node", {params: params}).then(function(response) {
        let data = response.data;
        self.g6 = data.elements // 修改，格式匹配
        self.loading = false
        self.render();
        
      });
    },
    render(){
      let self = this
      this.g6.nodes.forEach(function (node, idnex, array) {       
          node = Object.assign(node, node["data"]);
          delete node.data

          if(node["label"] == "HOST"){
              node.label = self.fittingString(node['hostname'],140,25)
              node["size"] = 140
              // node.label = node.hostname
              
              node.color = "#D3B7D8"
              node.style = {
                fill:'#FE929F	',
                lineWidth : 3,
                cursor : 'pointer'
                
              },
              node.labelCfg={
                position:'center',
                style:{
                  fill:'#ffffff',
                  weight:'bolder',
                  fontSize : 25,
                  cursor : 'pointer'
                  
                },
              },
              node.stateStyles={
                hover:{
                    fill:'#FA8072'
              },
                active:{
                  opacity:1,
                },
                inactive:{
                  opacity:0.1
                }
              }
          }
          else if(node["label"] == "IP"){
              node["label"] = node["ip"],
              node['ip'] = node['ip']
              node["size"] = 100
              node.label = self.fittingString(node.label, 100, 14);
              node.color = "#6495ED"
              node.style = {
                fill:'#3D82AB',
                lineWidth : 3,
                cursor : 'pointer'
                
                
              },
              node.labelCfg={
                position:'center',
                style:{
                  fill:'#ffffff',
                  fontSize : 14,
                  cursor : 'pointer'
                  
                },
              },
              node.stateStyles={
                hover:{
                    fill:'#b3e0e6'
              },
              active:{
                  opacity:1,
                },
                inactive:{
                  opacity:0.1
                }
              }
          }
          else if(node["status"] == "LISTEN"){
              node["label"] = node["port"]
              node["size"] = 60
              
              node.color ='	#CDC673'
              node.style={
                fill:'#FFB471',
                cursor : 'pointer'
              },
              node.labelCfg={
                position:'center',
                style:{
                  fill:'#383636',
                  cursor : 'pointer'
                },
              },
              node.stateStyles={
                hover:{
                    fill:'#EEEE00'
              },
              active:{
                  opacity:1,
                },
                inactive:{
                  opacity:0.1
                }
              }
          }   
          else if(node["status"] == "ESTAB"){
              node["label"] = node["port"]
              node["size"] = 60
              
              node.color ='#699C97'
              node.style={
                fill:'	#45BB89',
                cursor : 'pointer'
              },
              node.labelCfg={
                position:'center',
                style:{
                  fill:'#ffffff',
                },
              },
              node.stateStyles={
                hover:{
                    fill:'#ADFF2F',
                    cursor : 'pointer'
              },
              active:{
                  opacity:1,
                },
                inactive:{
                  opacity:0.1
                }
              }
          }   
          else if(node["status"] == "UNCONN"){
              node["label"] = node["port"]
              node["size"] = 60
              
              node.color ='#A52A2A'
              node.style={
                fill:'#FF6347',
                cursor : 'pointer'
              },
              node.labelCfg={
                position:'center',
                style:{
                  fill:'#ffffff',
                  cursor : 'pointer'
                },
              },
              node.stateStyles={
                hover:{
                    fill:'#FF6A6A'
              },
              active:{
                  opacity:1,
                },
                inactive:{
                  opacity:0.1
                }
              }
          }   

          else if(node["status"] == "CLOSE-WAIT"){
              node["label"] = node["port"]
              node["size"] = 60
              
              node.color ='#535D55	'
              node.style={
                fill:'#838B83',
                cursor : 'pointer'
              },
              node.labelCfg={
                position:'center',
                style:{
                  fill:'#ffffff',
                  cursor : 'pointer'
                },
              },
              node.stateStyles={
                hover:{
                    fill:'#FFFFF0'
              },active:{
                  opacity:1,
                },
                inactive:{
                  opacity:0.1
                }
              }
          }   
      })

      this.g6.edges.forEach(function (edge,idnex,array){
        edge = Object.assign(edge, edge['data']);
        delete edge.data
        edge.style = {
          endArrow: {
            path: G6.Arrow.triangle(15,10,22),
            d: 2,
            fill: '#999',
            
            }
        }
        edge.label = edge["relationship"]
        edge.stateStyles={
          stroke:'#999',
          active:{
                  opacity:1,
                },
                inactive:{
                  opacity:0.1
                }
          
        },
        edge.labelCfg={
          autoRotate: true,
          active:{
                  opacity:1,
                },
                inactive:{
                  opacity:0
                },
          style:{
            font:'Calibri',
            
          }
        }
      },
      )     
      console.log(this.g6.nodes)
      console.log(this.g6.edges)
      
      // this.graph.clear();

      this.graph.data({
        nodes: this.g6.nodes,
        edges: this.g6.edges
      });
      this.graph.changeData();
      this.graph.fitView();
      this.graph.render();
    },

    fittingString(str, maxWidth, fontSize) {
        let currentWidth = 0;
        let res = str;
        const pattern = new RegExp("[\u4E00-\u9FA5]+"); // distinguish the Chinese charactors and letters
        str.split('').forEach((letter, i) => {
          if (currentWidth > maxWidth) return;
          if (pattern.test(letter)) {
            // Chinese charactors
            currentWidth += fontSize;
          } else {
            // get the width of single letter according to the fontSize
            currentWidth += G6.Util.getLetterWidth(letter, fontSize);
          }
          if (currentWidth > maxWidth) {
            res = `${str.substr(0, i)}\n${str.substr(i)}`;
          }
        });
        return res;
    },

    getG6() {
      const contextMenu = new G6.Menu({
        getContent(graph) {
          console.log('graph',graph)
          return `
            <Button v-if="query.show_all_hosts" type="primary" shape="circle" style="margin-right:20px;;color:black" @click="get_All_Host_Data()">显示子节点</Button>
            <Button v-if="query.show_all_hosts" type="primary" shape="circle" style="margin-right:20px;;color:black" @click="get_All_Host_Data()">收起</Button>
          `;
        },
  handleMenuClick: (target, item) => {
    console.log(target, item)
  }
});
      const toolbar = new ToolBar()
      const grid = new Grid()
      const minimap = new Minimap({
          size: [ 500, 500 ],
          className: "minimap",
          type: 'delegate'
        });
      const width = document.getElementById('cy').clientWidth-10;
      const height = document.documentElement.clientHeight-10;
      const graph = new G6.Graph({
        container: 'cy',
        plugins:[grid,toolbar,contextMenu],//minimap],
        width,
        height,
        enabledStack: true,
        linkCenter: true,
        enabledStack:true,
        modes:{
          default:['drag-node', 'activate-relations','drag-canvas',
          //节点提示框
          {type:'tooltip',formatText(model){
            const text = 'INFO: '+ model.label + 
            '<br/>主机名: ' + model.hostname + 
            '<br/>主机 ID: ' + model.host_id + 
            '<br/>主机显示IP: ' + model.display_ip + 
            '<br/>IP地址: ' + model.ip + 
            '<br/>进程服务: ' + model.process + 
            '<br/>协议: ' + model.proto
            return text
          },
          offset: 40
          },
          { //边提示框
            type: 'edge-tooltip',formatText(model) {         // 边提示框文本内容
            const text = '<br/> 状态: ' + model.relationship;
            return text;
        },
        offset: 40
      },
          {type:'zoom-canvas',
          sensitivity:0.4},
          {
      },
        ],
        
        brush: [
      {
        type: 'brush-select',
        trigger: 'drag'
      }
    ],
        },
        layout: {
          type:'force',
          preventOverlap: true,
          fitView:true,
          animate:true,
          linkDistance: 200,
          nodeSpacing : 60,
          collideStrength: 0.6,
          endArrow:true

        },
        
        defaultNode: {
          color: '#5B8FF9',
          style: {
            lineWidth: 2,
            fill: '#C6E5FF',
          },
        },
        defaultEdge: {
          
        },
      },
      );

      this.graph = graph;
    },

  },
  
  mounted() {
    this.getG6();
    this.getNetMapData();    
    
  }
};
</script>
<style>
    /* 提示框的样式 */
    .g6-tooltip {
      top: 100%;
      left: 50%; 
      margin-left: -200;
      border: 1px solid #e2e2e2;
      border-radius: 20px;
      font-size: 12px;
      color: #545454;
      background-color: rgba(255, 255, 255, 0.9);
      padding: 5px 10px;
      box-shadow: rgb(174, 174, 174) 0px 0px 10px;
      text-align: left;
      position: relative;
      z-index: 5;
    }
</style>
<style>

    .g6-component-toolbar li {
    list-style-type: none !important;
  }
</style>

<style>
    /*中间的过度的横线*/
    .link-top {
        width: 50%;
        height: 1px;
        border-top: solid #ACC0D8 1px;
    }

    /*画一条再右边的竖线*/
    .link-right {
        width: 50px;
        height: 20%;
        border-right: solid #ACC0D8 1px;
    }

    </style>

<style>
#cy {
  width: 100%;
  height: 100%;
}

#legend {
	width: 240px;
	height:300px;
}
</style>


