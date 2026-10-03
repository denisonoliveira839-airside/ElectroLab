import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ElectroLab V2", page_icon="⚡", layout="wide")

HTML = r"""
<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}body{margin:0;background:#0b1220;color:#e5e7eb;font-family:Arial;overflow:hidden}
.top{height:58px;background:#111827;border-bottom:1px solid #334155;display:flex;gap:7px;align-items:center;padding:7px}
.brand{font-size:19px;font-weight:bold}.btn{background:#1e293b;color:#e5e7eb;border:1px solid #475569;border-radius:7px;padding:7px 10px}.green{background:#166534}.blue{background:#075985}
.main{height:calc(100vh - 58px);display:flex}.pal{width:205px;background:#111827;padding:8px;overflow:auto}.work{flex:1;min-width:0;display:flex;flex-direction:column}.right{width:245px;background:#111827;border-left:1px solid #334155;padding:8px;overflow:auto}
.group{border:1px solid #334155;border-radius:7px;margin-bottom:8px;overflow:hidden}.group b{display:block;padding:7px;background:#1e293b;font-size:12px}
.item{padding:7px;border-top:1px solid #334155;font-size:12px;cursor:grab}.item:hover{background:#263449}
.toolbar{height:42px;display:flex;gap:6px;align-items:center;padding:5px;border-bottom:1px solid #334155;overflow:auto}
.mode{background:#1e293b;color:#cbd5e1;border:1px solid #475569;border-radius:6px;padding:6px;white-space:nowrap}.active{background:#075985;border-color:#38bdf8;color:white}
.canvas{flex:1;position:relative}svg{width:100%;height:100%;background-color:#0b1220;background-image:linear-gradient(#172235 1px,transparent 1px),linear-gradient(90deg,#172235 1px,transparent 1px);background-size:20px 20px;touch-action:none}
.card{border:1px solid #334155;border-radius:7px;padding:9px;margin-bottom:8px;background:#172033}.small{font-size:11px;color:#94a3b8}.read{font-family:monospace;background:#020617;padding:8px;border-radius:5px;margin-top:5px;line-height:1.5}
.comp-body{fill:#1e293b;stroke:#94a3b8;stroke-width:2}.comp.on .comp-body{stroke:#22c55e}.term{fill:#f8fafc;stroke:#111827;stroke-width:2}.term.on{fill:#22c55e}.wire{fill:none;stroke:#64748b;stroke-width:3}.wire.on{stroke:#22c55e;filter:drop-shadow(0 0 4px #22c55e)}text{font-size:11px;fill:#e5e7eb;pointer-events:none}
input,select{width:100%;margin-top:4px;background:#0f172a;color:white;border:1px solid #475569;border-radius:5px;padding:5px}
@media(max-width:700px){.pal{display:none}.right{position:absolute;bottom:0;left:0;right:0;width:auto;height:185px;display:flex;gap:7px;z-index:4}.card{min-width:210px}.canvas{padding-bottom:185px}.top{flex-wrap:wrap;height:auto}.main{height:calc(100vh - 70px)}}
</style></head><body>
<div class="top"><span class="brand">⚡ ElectroLab V2</span><button class="btn" onclick="novo()">Novo</button>
<button class="btn" onclick="demo('dol')">Partida direta</button><button class="btn" onclick="demo('res')">Resistência</button>
<button class="btn" onclick="demo('lamp')">Residencial</button><button class="btn blue" onclick="salvar()">Salvar</button>
<button class="btn" onclick="document.querySelector('#abrir').click()">Abrir</button><input id="abrir" type="file" accept=".json" hidden onchange="abrir(event)">
<button id="run" class="btn green" onclick="simular()">▶ SIMULAR</button></div>
<div class="main">
<aside class="pal">
<div class="group"><b>FONTES / PROTEÇÃO</b><div class="item" draggable="true" data-t="source">⚡ Fonte AC 380 V</div><div class="item" draggable="true" data-t="breaker">▣ Disjuntor</div><div class="item" draggable="true" data-t="fuse">◇ Fusível</div><div class="item" draggable="true" data-t="ground">⏚ Terra PE</div><div class="item" draggable="true" data-t="neutral">N Neutro</div></div>
<div class="group"><b>COMANDO</b><div class="item" draggable="true" data-t="no">NA</div><div class="item" draggable="true" data-t="nc">NF</div><div class="item" draggable="true" data-t="contactor">K1 Contator</div><div class="item" draggable="true" data-t="thermal">FR Relé térmico</div><div class="item" draggable="true" data-t="relay">R Relé auxiliar</div><div class="item" draggable="true" data-t="thermostat">🌡 Termostato</div><div class="item" draggable="true" data-t="limit">Fim de curso</div></div>
<div class="group"><b>CARGAS / AUTOMAÇÃO</b><div class="item" draggable="true" data-t="lamp">💡 Lâmpada</div><div class="item" draggable="true" data-t="motor">M Motor 3~</div><div class="item" draggable="true" data-t="resistor">Ω Resistência</div><div class="item" draggable="true" data-t="vfd">VFD Inversor</div><div class="item" draggable="true" data-t="plc">PLC</div></div>
<div class="card small">Arraste para a bancada. Para ligar: clique em um borne e depois em outro. Duplo clique no componente para editar.</div>
</aside>
<section class="work"><div class="toolbar"><button class="mode active">🏠 Residencial</button><button class="mode">⚙️ Comando</button><button class="mode">🔌 Força</button><button class="mode">🤖 CLP</button><button class="mode">🧪 Diagnóstico</button></div><div id="canvas" class="canvas"><svg id="svg"></svg></div></section>
<aside class="right"><div class="card"><b>Estado</b><div id="estado" class="read">Desligada<br>Tensão: —<br>Corrente: —</div></div>
<div class="card"><b>Multímetro</b><div id="meter" class="read">Clique em dois bornes para medir.</div></div>
<div class="card" id="props"><b>Componente</b><div class="small">Nenhum selecionado.</div></div>
<div class="card"><b>Diagnóstico</b><div id="diag" class="small">Monte o circuito e simule.</div></div></aside></div>
<script>
const S={source:['Fonte AC',100,55,['L1','L2','L3','N']],breaker:['Disjuntor',90,45,['1','2']],fuse:['Fusível',85,45,['1','2']],ground:['Terra',70,45,['PE']],neutral:['Neutro',70,45,['N']],no:['Botão NA',90,45,['1','2']],nc:['Botão NF',90,45,['1','2']],contactor:['Contator K1',110,65,['A1','A2','13','14','21','22']],thermal:['Relé térmico',105,48,['95','96']],relay:['Relé auxiliar',105,58,['A1','A2','11','14']],thermostat:['Termostato NF',105,48,['1','2']],limit:['Fim de curso',95,45,['1','2']],lamp:['Lâmpada',90,55,['L','N']],motor:['Motor 3~',105,65,['U','V','W','PE']],resistor:['Resistência',105,55,['A','B']],vfd:['Inversor VFD',120,70,['L1','L2','L3','U','V','W']],plc:['CLP',110,65,['L+','M','I0','Q0']]};
let C=[],W=[],sel=null,start=null,run=false,id=1,drag=null,meterA=null,tool='wire';
function add(t,x,y){let q=S[t];let c={id:'C'+id++,t,x,y,n:q[0],w:q[1],h:q[2],ts:q[3],closed:!['no'].includes(t),coil:false,load:t==='motor'?2200:t==='resistor'?4000:t==='lamp'?100:0,v:t==='source'?380:380,set:70,temp:25};C.push(c);sel=c.id;return c}
function pos(c,i){let n=c.ts.length;return{x:c.x+(i%2?c.w:0),y:c.y+16+Math.floor(i/2)*((c.h-32)/Math.max(1,Math.ceil(n/2)-1))}}
function find(cid,i){let c=C.find(x=>x.id===cid);return c?pos(c,i):null}
function key(cid,i){return cid+':'+i}
function linked(cid,i){return W.some(w=>(w.a.c===cid&&w.a.i===i)||(w.b.c===cid&&w.b.i===i))}
function closed(c){if(['breaker','fuse','thermal','nc','thermostat','limit'].includes(c.t))return c.closed;if(c.t==='no')return c.closed;if(c.t==='contactor'||c.t==='relay')return c.coil;return true}
function render(){let svg=document.querySelector('#svg');svg.innerHTML='';
W.forEach(w=>{let a=find(w.a.c,w.a.i),b=find(w.b.c,w.b.i);if(!a||!b)return;let p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('d',`M${a.x} ${a.y} L${(a.x+b.x)/2} ${a.y} L${(a.x+b.x)/2} ${b.y} L${b.x} ${b.y}`);p.setAttribute('class','wire '+(w.on?'on':''));svg.appendChild(p)});
C.forEach(c=>{let g=document.createElementNS('http://www.w3.org/2000/svg','g');g.setAttribute('class','comp '+(c.on?'on':''));g.setAttribute('transform',`translate(${c.x},${c.y})`);g.onpointerdown=e=>beginDrag(e,c.id);g.ondblclick=e=>{sel=c.id;props()};
let r=document.createElementNS('http://www.w3.org/2000/svg','rect');r.setAttribute('width',c.w);r.setAttribute('height',c.h);r.setAttribute('rx',7);r.setAttribute('class','comp-body');g.appendChild(r);
let tx=document.createElementNS('http://www.w3.org/2000/svg','text');tx.setAttribute('x',c.w/2);tx.setAttribute('y',c.h/2+4);tx.setAttribute('text-anchor','middle');tx.textContent=c.n;g.appendChild(tx);
c.ts.forEach((t,i)=>{let p=pos(c,i),z=document.createElementNS('http://www.w3.org/2000/svg','circle');z.setAttribute('cx',p.x-c.x);z.setAttribute('cy',p.y-c.y);z.setAttribute('r',5);z.setAttribute('class','term '+(energ(cid=c.id,i)?'on':''));z.onclick=e=>{e.stopPropagation();borne(c.id,i)};g.appendChild(z);let tt=document.createElementNS('http://www.w3.org/2000/svg','text');tt.setAttribute('x',p.x-c.x+(i%2?-9:9));tt.setAttribute('y',p.y-c.y+3);tt.setAttribute('text-anchor',i%2?'end':'start');tt.textContent=t;g.appendChild(tt)});svg.appendChild(g)});
}
function energ(cid,i){return run&&(C.find(c=>c.id===cid)?.on||W.some(w=>w.on&&((w.a.c===cid&&w.a.i===i)||(w.b.c===cid&&w.b.i===i))))}
function borne(cid,i){
 if(tool==='meter'){
   if(!meterA){meterA={c:cid,i};document.querySelector('#meter').innerHTML='Ponta A selecionada. Clique no segundo borne.';return}
   let ea=energ(meterA.c,meterA.i),eb=energ(cid,i),v=ea&&eb?0:(ea||eb?380:0);
   document.querySelector('#meter').innerHTML='Ponta A: '+C.find(c=>c.id===meterA.c).ts[meterA.i]+'<br>Ponta B: '+C.find(c=>c.id===cid).ts[i]+'<br><b>Leitura: '+v+' V</b>';
   meterA=null; return;
 }
 if(start){
   if(!(start.c===cid&&start.i===i)){connect(start,{c:cid,i:i});}
   start=null; render(); return;
 }
 start={c:cid,i:i};
 document.querySelector('#meter').innerHTML='Borne A selecionado. Clique no borne B.'
}
function connect(a,b){if(!W.some(w=>(w.a.c===a.c&&w.a.i===a.i&&w.b.c===b.c&&w.b.i===b.i)||(w.b.c===a.c&&w.b.i===a.i&&w.a.c===b.c&&w.a.i===b.i)))W.push({a,b,on:false})}
document.querySelector('#svg').onclick=e=>{if(start&&e.target.tagName==='circle'){let s=start;start=null}else if(e.target.id==='svg'){sel=null;props()}}
function beginDrag(e,cid){sel=cid;props();let r=document.querySelector('#svg').getBoundingClientRect(),c=C.find(x=>x.id===cid);drag={cid,dx:e.clientX-r.left-c.x,dy:e.clientY-r.top-c.y}}
document.addEventListener('pointermove',e=>{if(!drag)return;let r=document.querySelector('#svg').getBoundingClientRect(),c=C.find(x=>x.id===drag.cid);c.x=Math.max(2,e.clientX-r.left-drag.dx);c.y=Math.max(2,e.clientY-r.top-drag.dy);render()});document.addEventListener('pointerup',()=>drag=null);
document.querySelectorAll('.item').forEach(x=>x.ondragstart=e=>e.dataTransfer.setData('t',x.dataset.t));
document.querySelector('#canvas').ondragover=e=>e.preventDefault();document.querySelector('#canvas').ondrop=e=>{let t=e.dataTransfer.getData('t'),r=document.querySelector('#svg').getBoundingClientRect();if(t)add(t,e.clientX-r.left-30,e.clientY-r.top-20),render(),props()};
function props(){let p=document.querySelector('#props'),c=C.find(x=>x.id===sel);if(!c){p.innerHTML='<b>Componente</b><div class="small">Nenhum selecionado.</div>';return}p.innerHTML='<b>'+c.n+'</b><label>Nome</label><input id="pn" value="'+c.n+'"><label>Potência W</label><input id="pl" type="number" value="'+c.load+'"><label>Tensão V</label><input id="pv" type="number" value="'+c.v+'"><button class="btn blue" style="margin-top:7px;width:100%" onclick="apply()">Aplicar</button>'}
function apply(){let c=C.find(x=>x.id===sel);if(!c)return;c.n=document.querySelector('#pn').value;c.load=+document.querySelector('#pl').value;c.v=+document.querySelector('#pv').value;render();props()}
function novo(){C=[];W=[];sel=null;run=false;id=1;document.querySelector('#run').textContent='▶ SIMULAR';render();props()}
function link(a,ai,b,bi){connect({c:a.id,i:ai},{c:b.id,i:bi})}
function demo(k){novo();if(k==='dol'){let s=add('source',60,130),q=add('breaker',210,130),fr=add('thermal',340,130),co=add('contactor',470,110),m=add('motor',650,120),b=add('no',330,290);link(s,0,q,0);link(q,1,fr,0);link(fr,1,co,2);link(co,3,m,0);link(s,1,m,1);link(s,0,b,0);link(b,1,co,0);link(s,1,co,1);b.closed=false}else if(k==='res'){let s=add('source',70,150),q=add('breaker',230,150),co=add('contactor',380,130),r=add('resistor',590,140),b=add('no',270,290),t=add('thermostat',440,290);link(s,0,q,0);link(q,1,co,2);link(co,3,r,0);link(r,1,s,1);link(s,0,b,0);link(b,1,co,0);link(s,1,co,1);link(co,4,t,0);link(t,1,s,1);b.closed=false}else{let s=add('source',70,160),q=add('breaker',240,160),b=add('no',380,160),l=add('lamp',540,150),n=add('neutral',390,290);link(s,0,q,0);link(q,1,b,0);link(b,1,l,0);link(l,1,n,0);link(n,0,s,1);b.closed=false}render()}
function simular(){run=!run;document.querySelector('#run').textContent=run?'■ PARAR':'▶ SIMULAR';if(!run){C.forEach(c=>{c.on=false;c.coil=false});W.forEach(w=>w.on=false);document.querySelector('#estado').innerHTML='Desligada<br>Tensão: —<br>Corrente: —';render();return}
let s=C.find(c=>c.t==='source'),power=new Set();if(s)for(let i=0;i<s.ts.length;i++)power.add(key(s.id,i));
let adj={};function ad(a,b){(adj[a]??=[]).push(b)}
W.forEach(w=>{ad(key(w.a.c,w.a.i),key(w.b.c,w.b.i));ad(key(w.b.c,w.b.i),key(w.a.c,w.a.i))});
C.forEach(c=>{let pairs=[];if(['breaker','fuse','no','nc','thermal','thermostat','limit','lamp','resistor'].includes(c.t))pairs=[[0,1]];if(c.t==='contactor')pairs=[[2,3],[4,5]];if(c.t==='relay')pairs=[[2,3]];pairs.forEach(p=>{if(closed(c)){ad(key(c.id,p[0]),key(c.id,p[1]));ad(key(c.id,p[1]),key(c.id,p[0]))}})});
let q=[...power],seen=new Set(q);while(q.length){let a=q.shift();(adj[a]||[]).forEach(b=>{if(!seen.has(b)){seen.add(b);power.add(b);q.push(b)}})}
C.forEach(c=>{c.on=c.ts.some((_,i)=>power.has(key(c.id,i)));if(['contactor','relay'].includes(c.t))c.coil=power.has(key(c.id,0))&&power.has(key(c.id,1))});
W.forEach(w=>w.on=power.has(key(w.a.c,w.a.i))&&power.has(key(w.b.c,w.b.i)));
let amps=0;C.forEach(c=>{if(c.on&&c.load)amps+=c.load/(c.v||380)});document.querySelector('#estado').innerHTML='🟢 Energizado<br>Tensão: 380 V<br>Corrente estimada: '+amps.toFixed(1)+' A';document.querySelector('#diag').innerHTML='🟢 Simulação didática concluída. Componentes energizados ficam verdes.';render()}
function salvar(){let b=new Blob([JSON.stringify({components:C,wires:W},null,2)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='electrolab-projeto.json';a.click()}
function abrir(e){let f=e.target.files[0],r=new FileReader();r.onload=()=>{let d=JSON.parse(r.result);C=d.components||[];W=d.wires||[];id=1+Math.max(0,...C.map(c=>parseInt(c.id.slice(1))||0));render()};r.readAsText(f)}
novo();
</script></body></html>"""
components.html(HTML, height=900, scrolling=False)
