(()=>{var Xt=Object.defineProperty;var Gt=Object.getOwnPropertyDescriptor;var c=(n,e,t,i)=>{for(var s=i>1?void 0:i?Gt(e,t):e,r=n.length-1,o;r>=0;r--)(o=n[r])&&(s=(i?o(e,t,s):o(s))||s);return i&&s&&Xt(e,t,s),s};var S=`
:host {
  --accent: #2563EB;
  --accent-strong: #1D4ED8;
  --accent-soft: #DBEAFE;
  --accent-ink: #1D4ED8;
  --surface: #FFFFFF;
  --surface-2: #F1F5F9;
  --text: #0F172A;
  --muted: #64748B;
  --line: #CBD5E1;
  --success: #16A34A;
  --success-soft: #DCFCE7;
  --success-ink: #166534;
  --danger: #DC2626;
  --radius-sm: 6px;
  --radius-md: 8px;
  --shadow-soft: 0 8px 22px rgba(15, 23, 42, 0.18);
}
`;var Z=globalThis,tt=Z.ShadowRoot&&(Z.ShadyCSS===void 0||Z.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,lt=Symbol(),wt=new WeakMap,z=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==lt)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(tt&&e===void 0){let i=t!==void 0&&t.length===1;i&&(e=wt.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&wt.set(t,e))}return e}toString(){return this.cssText}},T=n=>new z(typeof n=="string"?n:n+"",void 0,lt),E=(n,...e)=>{let t=n.length===1?n[0]:e.reduce((i,s,r)=>i+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+n[r+1],n[0]);return new z(t,n,lt)},$t=(n,e)=>{if(tt)n.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let i=document.createElement("style"),s=Z.litNonce;s!==void 0&&i.setAttribute("nonce",s),i.textContent=t.cssText,n.appendChild(i)}},ct=tt?n=>n:n=>n instanceof CSSStyleSheet?(e=>{let t="";for(let i of e.cssRules)t+=i.cssText;return T(t)})(n):n;var{is:Qt,defineProperty:Jt,getOwnPropertyDescriptor:Zt,getOwnPropertyNames:te,getOwnPropertySymbols:ee,getPrototypeOf:ie}=Object,et=globalThis,At=et.trustedTypes,se=At?At.emptyScript:"",ne=et.reactiveElementPolyfillSupport,K=(n,e)=>n,j={toAttribute(n,e){switch(e){case Boolean:n=n?se:null;break;case Object:case Array:n=n==null?n:JSON.stringify(n)}return n},fromAttribute(n,e){let t=n;switch(e){case Boolean:t=n!==null;break;case Number:t=n===null?null:Number(n);break;case Object:case Array:try{t=JSON.parse(n)}catch{t=null}}return t}},it=(n,e)=>!Qt(n,e),St={attribute:!0,type:String,converter:j,reflect:!1,useDefault:!1,hasChanged:it};Symbol.metadata??=Symbol("metadata"),et.litPropertyMetadata??=new WeakMap;var P=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=St){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let i=Symbol(),s=this.getPropertyDescriptor(e,i,t);s!==void 0&&Jt(this.prototype,e,s)}}static getPropertyDescriptor(e,t,i){let{get:s,set:r}=Zt(this.prototype,e)??{get(){return this[t]},set(o){this[t]=o}};return{get:s,set(o){let l=s?.call(this);r?.call(this,o),this.requestUpdate(e,l,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??St}static _$Ei(){if(this.hasOwnProperty(K("elementProperties")))return;let e=ie(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(K("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(K("properties"))){let t=this.properties,i=[...te(t),...ee(t)];for(let s of i)this.createProperty(s,t[s])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[i,s]of t)this.elementProperties.set(i,s)}this._$Eh=new Map;for(let[t,i]of this.elementProperties){let s=this._$Eu(t,i);s!==void 0&&this._$Eh.set(s,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let i=new Set(e.flat(1/0).reverse());for(let s of i)t.unshift(ct(s))}else e!==void 0&&t.push(ct(e));return t}static _$Eu(e,t){let i=t.attribute;return i===!1?void 0:typeof i=="string"?i:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return $t(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){let i=this.constructor.elementProperties.get(e),s=this.constructor._$Eu(e,i);if(s!==void 0&&i.reflect===!0){let r=(i.converter?.toAttribute!==void 0?i.converter:j).toAttribute(t,i.type);this._$Em=e,r==null?this.removeAttribute(s):this.setAttribute(s,r),this._$Em=null}}_$AK(e,t){let i=this.constructor,s=i._$Eh.get(e);if(s!==void 0&&this._$Em!==s){let r=i.getPropertyOptions(s),o=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:j;this._$Em=s;let l=o.fromAttribute(t,r.type);this[s]=l??this._$Ej?.get(s)??l,this._$Em=null}}requestUpdate(e,t,i,s=!1,r){if(e!==void 0){let o=this.constructor;if(s===!1&&(r=this[e]),i??=o.getPropertyOptions(e),!((i.hasChanged??it)(r,t)||i.useDefault&&i.reflect&&r===this._$Ej?.get(e)&&!this.hasAttribute(o._$Eu(e,i))))return;this.C(e,t,i)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:s,wrapped:r},o){i&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,o??t??this[e]),r!==!0||o!==void 0)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),s===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[s,r]of this._$Ep)this[s]=r;this._$Ep=void 0}let i=this.constructor.elementProperties;if(i.size>0)for(let[s,r]of i){let{wrapped:o}=r,l=this[s];o!==!0||this._$AL.has(s)||l===void 0||this.C(s,void 0,r,l)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(i=>i.hostUpdate?.()),this.update(t)):this._$EM()}catch(i){throw e=!1,this._$EM(),i}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};P.elementStyles=[],P.shadowRootOptions={mode:"open"},P[K("elementProperties")]=new Map,P[K("finalized")]=new Map,ne?.({ReactiveElement:P}),(et.reactiveElementVersions??=[]).push("2.1.2");var mt=globalThis,Tt=n=>n,st=mt.trustedTypes,Ct=st?st.createPolicy("lit-html",{createHTML:n=>n}):void 0,Mt="$lit$",k=`lit$${Math.random().toFixed(9).slice(2)}$`,It="?"+k,re=`<${It}>`,I=document,V=()=>I.createComment(""),Y=n=>n===null||typeof n!="object"&&typeof n!="function",ft=Array.isArray,oe=n=>ft(n)||typeof n?.[Symbol.iterator]=="function",pt=`[ 	
\f\r]`,F=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Pt=/-->/g,kt=/>/g,R=RegExp(`>|${pt}(?:([^\\s"'>=/]+)(${pt}*=${pt}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),Lt=/'/g,Ht=/"/g,Dt=/^(?:script|style|textarea|title)$/i,bt=n=>(e,...t)=>({_$litType$:n,strings:e,values:t}),y=bt(1),He=bt(2),Re=bt(3),D=Symbol.for("lit-noChange"),m=Symbol.for("lit-nothing"),Rt=new WeakMap,M=I.createTreeWalker(I,129);function Nt(n,e){if(!ft(n)||!n.hasOwnProperty("raw"))throw Error("invalid template strings array");return Ct!==void 0?Ct.createHTML(e):e}var ae=(n,e)=>{let t=n.length-1,i=[],s,r=e===2?"<svg>":e===3?"<math>":"",o=F;for(let l=0;l<t;l++){let a=n[l],p,u,h=-1,_=0;for(;_<a.length&&(o.lastIndex=_,u=o.exec(a),u!==null);)_=o.lastIndex,o===F?u[1]==="!--"?o=Pt:u[1]!==void 0?o=kt:u[2]!==void 0?(Dt.test(u[2])&&(s=RegExp("</"+u[2],"g")),o=R):u[3]!==void 0&&(o=R):o===R?u[0]===">"?(o=s??F,h=-1):u[1]===void 0?h=-2:(h=o.lastIndex-u[2].length,p=u[1],o=u[3]===void 0?R:u[3]==='"'?Ht:Lt):o===Ht||o===Lt?o=R:o===Pt||o===kt?o=F:(o=R,s=void 0);let v=o===R&&n[l+1].startsWith("/>")?" ":"";r+=o===F?a+re:h>=0?(i.push(p),a.slice(0,h)+Mt+a.slice(h)+k+v):a+k+(h===-2?l:v)}return[Nt(n,r+(n[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),i]},W=class n{constructor({strings:e,_$litType$:t},i){let s;this.parts=[];let r=0,o=0,l=e.length-1,a=this.parts,[p,u]=ae(e,t);if(this.el=n.createElement(p,i),M.currentNode=this.el.content,t===2||t===3){let h=this.el.content.firstChild;h.replaceWith(...h.childNodes)}for(;(s=M.nextNode())!==null&&a.length<l;){if(s.nodeType===1){if(s.hasAttributes())for(let h of s.getAttributeNames())if(h.endsWith(Mt)){let _=u[o++],v=s.getAttribute(h).split(k),N=/([.?@])?(.*)/.exec(_);a.push({type:1,index:r,name:N[2],strings:v,ctor:N[1]==="."?ht:N[1]==="?"?ut:N[1]==="@"?gt:O}),s.removeAttribute(h)}else h.startsWith(k)&&(a.push({type:6,index:r}),s.removeAttribute(h));if(Dt.test(s.tagName)){let h=s.textContent.split(k),_=h.length-1;if(_>0){s.textContent=st?st.emptyScript:"";for(let v=0;v<_;v++)s.append(h[v],V()),M.nextNode(),a.push({type:2,index:++r});s.append(h[_],V())}}}else if(s.nodeType===8)if(s.data===It)a.push({type:2,index:r});else{let h=-1;for(;(h=s.data.indexOf(k,h+1))!==-1;)a.push({type:7,index:r}),h+=k.length-1}r++}}static createElement(e,t){let i=I.createElement("template");return i.innerHTML=e,i}};function U(n,e,t=n,i){if(e===D)return e;let s=i!==void 0?t._$Co?.[i]:t._$Cl,r=Y(e)?void 0:e._$litDirective$;return s?.constructor!==r&&(s?._$AO?.(!1),r===void 0?s=void 0:(s=new r(n),s._$AT(n,t,i)),i!==void 0?(t._$Co??=[])[i]=s:t._$Cl=s),s!==void 0&&(e=U(n,s._$AS(n,e.values),s,i)),e}var dt=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:i}=this._$AD,s=(e?.creationScope??I).importNode(t,!0);M.currentNode=s;let r=M.nextNode(),o=0,l=0,a=i[0];for(;a!==void 0;){if(o===a.index){let p;a.type===2?p=new X(r,r.nextSibling,this,e):a.type===1?p=new a.ctor(r,a.name,a.strings,this,e):a.type===6&&(p=new yt(r,this,e)),this._$AV.push(p),a=i[++l]}o!==a?.index&&(r=M.nextNode(),o++)}return M.currentNode=I,s}p(e){let t=0;for(let i of this._$AV)i!==void 0&&(i.strings!==void 0?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}},X=class n{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,s){this.type=2,this._$AH=m,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=U(this,e,t),Y(e)?e===m||e==null||e===""?(this._$AH!==m&&this._$AR(),this._$AH=m):e!==this._$AH&&e!==D&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):oe(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==m&&Y(this._$AH)?this._$AA.nextSibling.data=e:this.T(I.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:i}=e,s=typeof i=="number"?this._$AC(e):(i.el===void 0&&(i.el=W.createElement(Nt(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(t);else{let r=new dt(s,this),o=r.u(this.options);r.p(t),this.T(o),this._$AH=r}}_$AC(e){let t=Rt.get(e.strings);return t===void 0&&Rt.set(e.strings,t=new W(e)),t}k(e){ft(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,i,s=0;for(let r of e)s===t.length?t.push(i=new n(this.O(V()),this.O(V()),this,this.options)):i=t[s],i._$AI(r),s++;s<t.length&&(this._$AR(i&&i._$AB.nextSibling,s),t.length=s)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let i=Tt(e).nextSibling;Tt(e).remove(),e=i}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},O=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,s,r){this.type=1,this._$AH=m,this._$AN=void 0,this.element=e,this.name=t,this._$AM=s,this.options=r,i.length>2||i[0]!==""||i[1]!==""?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=m}_$AI(e,t=this,i,s){let r=this.strings,o=!1;if(r===void 0)e=U(this,e,t,0),o=!Y(e)||e!==this._$AH&&e!==D,o&&(this._$AH=e);else{let l=e,a,p;for(e=r[0],a=0;a<r.length-1;a++)p=U(this,l[i+a],t,a),p===D&&(p=this._$AH[a]),o||=!Y(p)||p!==this._$AH[a],p===m?e=m:e!==m&&(e+=(p??"")+r[a+1]),this._$AH[a]=p}o&&!s&&this.j(e)}j(e){e===m?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},ht=class extends O{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===m?void 0:e}},ut=class extends O{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==m)}},gt=class extends O{constructor(e,t,i,s,r){super(e,t,i,s,r),this.type=5}_$AI(e,t=this){if((e=U(this,e,t,0)??m)===D)return;let i=this._$AH,s=e===m&&i!==m||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,r=e!==m&&(i===m||s);s&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},yt=class{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){U(this,e)}};var le=mt.litHtmlPolyfillSupport;le?.(W,X),(mt.litHtmlVersions??=[]).push("3.3.3");var Ut=(n,e,t)=>{let i=t?.renderBefore??e,s=i._$litPart$;if(s===void 0){let r=t?.renderBefore??null;i._$litPart$=s=new X(e.insertBefore(V(),r),r,void 0,t??{})}return s._$AI(n),s};var vt=globalThis,f=class extends P{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Ut(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return D}};f._$litElement$=!0,f.finalized=!0,vt.litElementHydrateSupport?.({LitElement:f});var ce=vt.litElementPolyfillSupport;ce?.({LitElement:f});(vt.litElementVersions??=[]).push("4.2.2");var $=n=>(e,t)=>{t!==void 0?t.addInitializer(()=>{customElements.define(n,e)}):customElements.define(n,e)};var pe={attribute:!0,type:String,converter:j,reflect:!1,hasChanged:it},de=(n=pe,e,t)=>{let{kind:i,metadata:s}=t,r=globalThis.litPropertyMetadata.get(s);if(r===void 0&&globalThis.litPropertyMetadata.set(s,r=new Map),i==="setter"&&((n=Object.create(n)).wrapped=!0),r.set(t.name,n),i==="accessor"){let{name:o}=t;return{set(l){let a=e.get.call(this);e.set.call(this,l),this.requestUpdate(o,a,n,!0,l)},init(l){return l!==void 0&&this.C(o,void 0,n,l),l}}}if(i==="setter"){let{name:o}=t;return function(l){let a=this[o];e.call(this,l),this.requestUpdate(o,a,n,!0,l)}}throw Error("Unsupported decorator location: "+i)};function d(n){return(e,t)=>typeof t=="object"?de(n,e,t):((i,s,r)=>{let o=s.hasOwnProperty(r);return s.constructor.createProperty(r,i),o?Object.getOwnPropertyDescriptor(s,r):void 0})(n,e,t)}function x(n){return d({...n,state:!0,attribute:!1})}var b=class extends f{constructor(){super(...arguments);this.open=!1;this.graphEntities=[];this.tagsetProperties={};this.placeholder="Capture name (optional)";this.nameLabel="Capture name";this.viewportLabel="Visible area";this.regionLabel="Select area";this.attachHeading="Attach to entity (optional)";this.chooseEntityLabel="Don't attach";this.propertyPlaceholder="Property name";this.defaultPropertyKey="Capture \xE9cran";this._selectedEntityId="";this._onEntityChange=t=>{this._selectedEntityId=t.target.value}}get captureName(){return this.input()?.value.trim()||""}set captureName(t){let i=this.input();i&&(i.value=t)}ensureCaptureName(t){let i=this.input();i&&!i.value.trim()&&(i.value=t)}reset(){this.captureName="",this._selectedEntityId="";let t=this.propertyInput();t&&(t.value="");let i=this.entitySelect();i&&(i.value=""),this.open=!1}get _entities(){return this.graphEntities.filter(t=>String(t.id??"").trim())}get _propertySuggestions(){let t=this._entities.find(o=>String(o.id??"").trim()===this._selectedEntityId.trim());if(!t)return[];let i=new Set,s=[],r=o=>{let l=String(o??"").trim(),a=l.toLowerCase();!l||i.has(a)||(i.add(a),s.push(l))};for(let o of t.tags??[])for(let l of this.tagsetProperties[String(o??"").trim()]??[])r(l);for(let o of t.propertyKeys??[])r(o);return s}get _attach(){if(!this._selectedEntityId)return null;let t=this.propertyInput()?.value.trim()||this.defaultPropertyKey;return{entityId:this._selectedEntityId,propertyKey:t,propertyType:""}}firstUpdated(){this.renderRoot.querySelectorAll("[data-scope]").forEach(t=>{t.addEventListener("click",()=>{this.choose(t.dataset.scope)})})}render(){let t=this._entities.length>0;return y`
      <input
        class="name-input"
        type="text"
        maxlength="120"
        placeholder=${this.placeholder}
        aria-label=${this.nameLabel}
      >
      ${t?y`
            <div class="attach">
              <div class="attach-heading">${this.attachHeading}</div>
              <select
                class="entity-select"
                aria-label=${this.attachHeading}
                @change=${this._onEntityChange}
              >
                <option value="">${this.chooseEntityLabel}</option>
                ${this._entities.map(i=>y`
                    <option value=${i.id}>
                      ${i.label||i.id}
                    </option>
                  `)}
              </select>
              <input
                class="prop-input"
                type="text"
                maxlength="100"
                placeholder=${this.propertyPlaceholder}
                list="__sx-capture-props"
              >
              <datalist id="__sx-capture-props">
                ${this._propertySuggestions.map(i=>y`<option value=${i}></option>`)}
              </datalist>
            </div>
          `:""}
      <button type="button" data-scope="viewport">${this.viewportLabel}</button>
      <button type="button" data-scope="region">${this.regionLabel}</button>
    `}input(){return this.renderRoot.querySelector(".name-input")}propertyInput(){return this.renderRoot.querySelector(".prop-input")}entitySelect(){return this.renderRoot.querySelector(".entity-select")}choose(t){this.open=!1,this.dispatchEvent(new CustomEvent("synthesix-capture-choice",{bubbles:!0,composed:!0,detail:{scope:t,captureName:this.captureName,attach:this._attach}}))}};b.styles=E`
    ${T(S)}

    :host {
      box-sizing: border-box;
      display: none;
      position: absolute;
      right: 0;
      bottom: 50px;
      width: 220px;
      padding: 6px;
      border: 1px solid var(--line, #cbd5e1);
      border-radius: var(--radius-sm, 6px);
      background: var(--surface, #ffffff);
      box-shadow: 0 14px 32px rgba(15, 23, 42, 0.24);
      color: var(--text, #0f172a);
      font: 600 13px/1.25 system-ui, Arial, sans-serif;
    }

    :host([open]) {
      display: block;
    }

    input,
    select {
      all: initial;
      box-sizing: border-box;
      display: block;
      width: 100%;
      margin-bottom: 5px;
      padding: 8px 9px;
      border: 1px solid var(--line, #cbd5e1);
      border-radius: 4px;
      background: var(--surface, #ffffff);
      color: var(--text, #0f172a);
      font: 500 13px/1.2 system-ui, Arial, sans-serif;
    }

    .attach {
      margin: 2px 0 6px;
      padding-top: 6px;
      border-top: 1px solid var(--line, #cbd5e1);
    }

    .attach-heading {
      margin-bottom: 4px;
      color: var(--text-muted, #64748b);
      font: 700 11px/1.2 system-ui, Arial, sans-serif;
      text-transform: uppercase;
      letter-spacing: 0.02em;
    }

    button {
      all: initial;
      box-sizing: border-box;
      display: block;
      width: 100%;
      padding: 9px 10px;
      border-radius: 4px;
      color: var(--text, #0f172a);
      cursor: pointer;
      font: 600 13px/1.2 system-ui, Arial, sans-serif;
    }

    button:hover,
    button:focus-visible {
      background: var(--accent-soft, #eff6ff);
      color: var(--accent-ink, #1d4ed8);
      outline: none;
    }
  `,c([d({type:Boolean,reflect:!0})],b.prototype,"open",2),c([d({attribute:!1})],b.prototype,"graphEntities",2),c([d({attribute:!1})],b.prototype,"tagsetProperties",2),c([d()],b.prototype,"placeholder",2),c([d({attribute:"name-label"})],b.prototype,"nameLabel",2),c([d({attribute:"viewport-label"})],b.prototype,"viewportLabel",2),c([d({attribute:"region-label"})],b.prototype,"regionLabel",2),c([d({attribute:"attach-heading"})],b.prototype,"attachHeading",2),c([d({attribute:"choose-entity-label"})],b.prototype,"chooseEntityLabel",2),c([d({attribute:"property-placeholder"})],b.prototype,"propertyPlaceholder",2),c([d({attribute:"default-property-key"})],b.prototype,"defaultPropertyKey",2),c([x()],b.prototype,"_selectedEntityId",2),b=c([$("sx-overlay-capture-menu")],b);var B=class extends f{constructor(){super(...arguments);this.label=""}render(){return y`<button type="button"></button>`}updated(){let t=this.renderRoot.querySelector("button");if(!t)return;let i=this.getAttribute("label")||this.label;t.textContent=i,t.setAttribute("aria-label",i)}};B.styles=E`
    ${T(S)}

    :host {
      box-sizing: border-box;
      display: none;
      position: fixed;
      left: 0;
      top: 0;
      z-index: 2147483647;
    }

    button {
      all: initial;
      box-sizing: border-box;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      max-width: min(260px, calc(100vw - 16px));
      padding: 7px 9px;
      border: 1px solid var(--accent-strong, #1d4ed8);
      border-radius: 999px;
      background: var(--accent, #2563eb);
      color: #ffffff;
      box-shadow: 0 10px 26px rgba(15, 23, 42, 0.26);
      cursor: pointer;
      font: 700 12px/1.1 system-ui, Arial, sans-serif;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    button:hover,
    button:focus-visible {
      background: var(--accent-strong, #1d4ed8);
      outline: 3px solid rgba(6, 182, 212, 0.45);
      outline-offset: 2px;
    }
  `,c([d()],B.prototype,"label",2),B=c([$("sx-overlay-selection-trigger")],B);var q=class extends f{constructor(){super(...arguments);this.hint="Drag to select evidence \xB7 Esc to cancel";this._selecting=!1;this._startX=0;this._startY=0;this._onKeyDown=t=>{t.key==="Escape"&&(t.preventDefault(),this._emitCancel())};this._onPointerDown=t=>{t.preventDefault(),this._selecting=!0,this._startX=t.clientX,this._startY=t.clientY;let i=this._boxEl;i&&i.classList.add("is-active");try{this.setPointerCapture(t.pointerId)}catch{}};this._onPointerMove=t=>{if(!this._selecting)return;let i=this._boxEl;if(!i)return;let s=Math.min(this._startX,t.clientX),r=Math.min(this._startY,t.clientY);i.style.left=`${s}px`,i.style.top=`${r}px`,i.style.width=`${Math.abs(t.clientX-this._startX)}px`,i.style.height=`${Math.abs(t.clientY-this._startY)}px`};this._onPointerUp=t=>{if(!this._selecting)return;this._selecting=!1;let i=Math.min(this._startX,t.clientX),s=Math.min(this._startY,t.clientY),r=Math.abs(t.clientX-this._startX),o=Math.abs(t.clientY-this._startY);if(r<8||o<8){this._emitCancel();return}this.dispatchEvent(new CustomEvent("synthesix-region-selected",{bubbles:!0,composed:!0,detail:{x:i+window.scrollX,y:s+window.scrollY,width:r,height:o}}))}}connectedCallback(){super.connectedCallback(),document.addEventListener("keydown",this._onKeyDown,!0),this.addEventListener("pointerdown",this._onPointerDown),this.addEventListener("pointermove",this._onPointerMove),this.addEventListener("pointerup",this._onPointerUp)}disconnectedCallback(){document.removeEventListener("keydown",this._onKeyDown,!0),super.disconnectedCallback()}get _boxEl(){return this.renderRoot.querySelector(".box")}_emitCancel(){this.dispatchEvent(new CustomEvent("synthesix-region-cancel",{bubbles:!0,composed:!0}))}render(){return y`
      <div class="hint">${this.hint}</div>
      <div class="box"></div>
    `}};q.styles=E`
    :host {
      all: initial;
      display: block;
      position: fixed;
      inset: 0;
      z-index: 2147483647;
      cursor: crosshair;
      background: rgba(15, 23, 42, 0.16);
      user-select: none;
      touch-action: none;
    }
    .hint {
      position: fixed;
      top: 16px;
      left: 50%;
      transform: translateX(-50%);
      padding: 9px 12px;
      border-radius: 6px;
      background: #0f172a;
      color: #ffffff;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.3);
      font: 600 13px Arial, sans-serif;
      pointer-events: none;
    }
    .box {
      display: none;
      position: fixed;
      border: 2px solid #06b6d4;
      background: rgba(6, 182, 212, 0.12);
      box-shadow: 0 0 0 9999px rgba(15, 23, 42, 0.38);
      pointer-events: none;
    }
    .box.is-active {
      display: block;
    }
  `,c([d()],q.prototype,"hint",2),q=c([$("sx-overlay-selection-box")],q);var Ot={text:"Texte",number:"Nombre",date:"Date",datetime:"Date/heure",geo:"G\xE9o",country:"Pays",link:"Lien"},g=class extends f{constructor(){super(...arguments);this.baseTagsets=[];this.existingTags=[];this.tagsetProperties={};this.tagsetPropertyTypes={};this.graphEntities=[];this.heading="Ajouter \xE0 l'enqu\xEAte";this.createHeading="Cr\xE9er une entit\xE9";this.typePlaceholder="Type d'entit\xE9...";this.createLabel="Cr\xE9er";this.attachHeading="Ajouter comme propri\xE9t\xE9";this.chooseEntityLabel="Choisir une entit\xE9...";this.propertyPlaceholder="Type de l'information";this.attachLabel="Rattacher";this._selectedText="";this._selectedEntityId="";this._selectedPropertyType="";this._triggerVisible=!1;this._menuVisible=!1;this._triggerLeft=0;this._triggerTop=0;this._menuLeft=0;this._menuTop=0;this._onDocMouseUp=t=>{t.composedPath().includes(this)||window.setTimeout(()=>this._showTrigger(),0)};this._onDocClick=t=>{t.composedPath().includes(this)||this._close()};this._onDocKeyDown=t=>{t.key==="Escape"&&this._close()};this._onTriggerClick=()=>{let i=this.renderRoot.querySelector(".trigger")?.getBoundingClientRect(),s=i?i.left:this._triggerLeft,r=i?i.bottom+6:this._triggerTop,o=this._selectionText()||this._selectedText;if(!o){this._close();return}this._selectedText=o,this._selectedEntityId="",this._menuLeft=Math.min(Math.max(s,8),Math.max(8,window.innerWidth-316)),this._menuTop=Math.min(Math.max(r,8),Math.max(8,window.innerHeight-320)),this._triggerVisible=!1,this._menuVisible=!0};this._onEntityChange=t=>{this._selectedEntityId=t.target.value;let i=this.renderRoot.querySelector(".prop-input");this._selectedPropertyType=this._suggestedPropertyType(i?.value??"")};this._onPropertyInput=t=>{this._selectedPropertyType=this._suggestedPropertyType(t.target.value)};this._onPropertyTypeChange=t=>{this._selectedPropertyType=t.target.value};this._onCreate=()=>{let i=(this.renderRoot.querySelector(".type-input")?.value??"").trim();if(!i)return;let s=this._selectedText;this._close(),s&&this.dispatchEvent(new CustomEvent("synthesix-entity-create",{bubbles:!0,composed:!0,detail:{label:s,category:i}}))};this._onTypeKeydown=t=>{t.key==="Enter"&&(t.preventDefault(),this._onCreate())};this._onAttach=()=>{let t=this.renderRoot.querySelector(".entity-select"),i=this.renderRoot.querySelector(".prop-input"),s=t?.value??"",r=(i?.value??"").trim(),o=this._selectedPropertyType,l=this._selectedText;this._close(),!(!l||!s||!r)&&this.dispatchEvent(new CustomEvent("synthesix-entity-attach",{bubbles:!0,composed:!0,detail:{label:l,entityId:s,propertyKey:r,propertyType:o}}))};this._onPropKeydown=t=>{t.key==="Enter"&&(t.preventDefault(),this._onAttach())};this._stop=t=>t.stopPropagation()}connectedCallback(){super.connectedCallback(),document.addEventListener("mouseup",this._onDocMouseUp),document.addEventListener("click",this._onDocClick),document.addEventListener("keydown",this._onDocKeyDown,!0)}disconnectedCallback(){document.removeEventListener("mouseup",this._onDocMouseUp),document.removeEventListener("click",this._onDocClick),document.removeEventListener("keydown",this._onDocKeyDown,!0),super.disconnectedCallback()}_dedup(t){let i=new Set,s=[];for(let r of t){let o=String(r??"").trim(),l=o.toLowerCase();!o||i.has(l)||(i.add(l),s.push(o))}return s}get _typeSuggestions(){return this._dedup([...this.baseTagsets,...this.existingTags])}get _entities(){return this.graphEntities.filter(t=>String(t.id??"").trim())}get _propertySuggestions(){let t=this._entities.find(s=>String(s.id??"").trim()===String(this._selectedEntityId).trim());if(!t)return[];let i=[];for(let s of t.tags??[])i.push(...this.tagsetProperties[String(s??"").trim()]??[]);return i.push(...t.propertyKeys??[]),this._dedup(i)}_suggestedPropertyType(t){let i=String(t??"").trim().toLowerCase();if(!i)return"";let s=this._entities.find(r=>String(r.id??"").trim()===String(this._selectedEntityId).trim());for(let r of s?.tags??[]){let o=this.tagsetPropertyTypes[String(r??"").trim()]??{};for(let[l,a]of Object.entries(o))if(l.trim().toLowerCase()===i)return Object.prototype.hasOwnProperty.call(Ot,a)?a:""}return""}_selectionText(){return String(window.getSelection()?.toString()??"").replace(/\s+/g," ").trim().slice(0,200)}_close(){this._menuVisible=!1,this._triggerVisible=!1,this._selectedEntityId="",this._selectedPropertyType="";let t=this.renderRoot.querySelector(".type-input"),i=this.renderRoot.querySelector(".prop-input"),s=this.renderRoot.querySelector("select");t&&(t.value=""),i&&(i.value=""),s&&(s.value="")}_showTrigger(){let t=this._selectionText(),i=window.getSelection();if(!t||!i||i.rangeCount===0){this._close();return}let s=i.getRangeAt(0).getBoundingClientRect();if(!s||!s.width&&!s.height){this._close();return}this._selectedText=t,this._triggerLeft=Math.min(Math.max(s.left,8),Math.max(8,window.innerWidth-150)),this._triggerTop=Math.max(8,s.top-38),this._menuVisible=!1,this._triggerVisible=!0}render(){let t=this._entities.length>0,i=`display:${this._triggerVisible?"block":"none"};left:${this._triggerLeft}px;top:${this._triggerTop}px;`,s=`left:${this._menuLeft}px;top:${this._menuTop}px;`;return y`
      <sx-overlay-selection-trigger
        class="trigger"
        style=${i}
        label=${this.heading}
        @click=${this._onTriggerClick}
      ></sx-overlay-selection-trigger>
      <div
        class="menu ${this._menuVisible?"is-visible":""}"
        style=${s}
        @mousedown=${this._stop}
        @mouseup=${this._stop}
        @click=${this._stop}
      >
        <div class="title">${this.heading}</div>
        <div class="preview">${this._selectedText}</div>
        <div class="create-title">${this.createHeading}</div>
        <div class="row">
          <input
            class="type-input"
            type="text"
            maxlength="50"
            placeholder=${this.typePlaceholder}
            list="__sx-entity-types"
            @keydown=${this._onTypeKeydown}
          >
          <button class="create-btn" type="button" @click=${this._onCreate}>
            ${this.createLabel}
          </button>
          <datalist id="__sx-entity-types">
            ${this._typeSuggestions.map(r=>y`<option value=${r}></option>`)}
          </datalist>
        </div>
        <div class="attach">
          <div class="attach-title">${this.attachHeading}</div>
          <select
            class="entity-select"
            ?disabled=${!t}
            @change=${this._onEntityChange}
          >
            <option value="">${this.chooseEntityLabel}</option>
            ${this._entities.map(r=>y`<option value=${r.id}>${r.label||r.id}</option>`)}
          </select>
          <input
            class="prop-input"
            type="text"
            maxlength="100"
            placeholder=${this.propertyPlaceholder}
            list="__sx-entity-props"
            @input=${this._onPropertyInput}
            @keydown=${this._onPropKeydown}
          >
          <datalist id="__sx-entity-props">
            ${this._propertySuggestions.map(r=>y`<option value=${r}></option>`)}
          </datalist>
          <select
            class="property-type-select"
            aria-label="Property type"
            .value=${this._selectedPropertyType}
            ?disabled=${!t}
            @change=${this._onPropertyTypeChange}
          >
            <option value="">Type auto</option>
            ${Object.entries(Ot).map(([r,o])=>y`<option value=${r}>${o}</option>`)}
          </select>
          <button
            class="attach-btn"
            type="button"
            ?disabled=${!t}
            @click=${this._onAttach}
          >
            ${this.attachLabel}
          </button>
        </div>
      </div>
    `}};g.styles=E`
    :host {
      all: initial;
    }
    .trigger {
      position: fixed;
      z-index: 2147483647;
    }
    .menu {
      box-sizing: border-box;
      display: none;
      position: fixed;
      width: 318px;
      max-height: 430px;
      padding: 10px;
      border: 1px solid rgba(34, 211, 238, 0.38);
      border-left: 3px solid #22d3ee;
      border-radius: 10px;
      background: #0f172a;
      box-shadow: 0 18px 42px rgba(2, 6, 23, 0.38);
      color: #e5edf8;
      font: 600 13px system-ui, Arial, sans-serif;
      z-index: 2147483647;
    }
    .menu.is-visible {
      display: block;
    }
    .title {
      padding: 1px 2px 2px;
      color: #67e8f9;
      font: 800 12px system-ui, Arial, sans-serif;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .preview {
      overflow: hidden;
      margin: 0 0 8px;
      padding: 0 2px;
      color: #f8fafc;
      font: 800 13px system-ui, Arial, sans-serif;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .create-title,
    .attach-title {
      padding: 0 2px 5px;
      color: #9fb0c6;
      font: 800 11px system-ui, Arial, sans-serif;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }
    .row {
      display: flex;
      gap: 6px;
      padding: 5px 0 8px;
    }
    input,
    select {
      all: initial;
      box-sizing: border-box;
      display: block;
      width: 100%;
      padding: 8px 9px;
      border: 1px solid #334155;
      border-radius: 7px;
      background: #111c2f;
      color: #f8fafc;
      font: 600 13px system-ui, Arial, sans-serif;
    }
    input::placeholder {
      color: #94a3b8;
    }
    input:focus,
    select:focus {
      border-color: #22d3ee;
      box-shadow: 0 0 0 2px rgba(34, 211, 238, 0.18);
    }
    .type-input {
      flex: 1;
      min-width: 0;
    }
    .attach {
      margin-top: 3px;
      padding-top: 9px;
      border-top: 1px solid #243349;
    }
    .attach .prop-input,
    .entity-select,
    .property-type-select {
      margin-bottom: 6px;
    }
    button {
      all: initial;
      box-sizing: border-box;
      border-radius: 7px;
      cursor: pointer;
      font: 800 13px system-ui, Arial, sans-serif;
      color: #ffffff;
    }
    .create-btn {
      padding: 8px 10px;
      background: #2563eb;
    }
    .attach-btn {
      display: block;
      width: 100%;
      padding: 9px 10px;
      border: 1px solid rgba(34, 211, 238, 0.42);
      background: #2563eb;
      text-align: center;
    }
    .create-btn:hover,
    .attach-btn:hover {
      background: #1d4ed8;
    }
    button[disabled] {
      opacity: 0.55;
      cursor: not-allowed;
    }
  `,c([d({attribute:!1})],g.prototype,"baseTagsets",2),c([d({attribute:!1})],g.prototype,"existingTags",2),c([d({attribute:!1})],g.prototype,"tagsetProperties",2),c([d({attribute:!1})],g.prototype,"tagsetPropertyTypes",2),c([d({attribute:!1})],g.prototype,"graphEntities",2),c([d()],g.prototype,"heading",2),c([d()],g.prototype,"createHeading",2),c([d({attribute:"type-placeholder"})],g.prototype,"typePlaceholder",2),c([d({attribute:"create-label"})],g.prototype,"createLabel",2),c([d({attribute:"attach-heading"})],g.prototype,"attachHeading",2),c([d({attribute:"choose-entity-label"})],g.prototype,"chooseEntityLabel",2),c([d({attribute:"property-placeholder"})],g.prototype,"propertyPlaceholder",2),c([d({attribute:"attach-label"})],g.prototype,"attachLabel",2),c([x()],g.prototype,"_selectedText",2),c([x()],g.prototype,"_selectedEntityId",2),c([x()],g.prototype,"_selectedPropertyType",2),c([x()],g.prototype,"_triggerVisible",2),c([x()],g.prototype,"_menuVisible",2),c([x()],g.prototype,"_triggerLeft",2),c([x()],g.prototype,"_triggerTop",2),c([x()],g.prototype,"_menuLeft",2),c([x()],g.prototype,"_menuTop",2),g=c([$("sx-overlay-entity-menu")],g);var w=class extends f{constructor(){super(...arguments);this.variant="primary";this.state="idle";this.label="";this.titleText="";this.ariaText="";this.icon="none";this.iconOnly=!1;this.disabled=!1}render(){return y`
      <button
        type="button"
      >
        ${this.renderIcon()}
        <span data-label></span>
      </button>
    `}updated(){let t=this.renderRoot.querySelector("button"),i=this.getAttribute("label")||this.label;if(!t)return;let s=t.querySelector("[data-label]");s&&(s.textContent=i),t.disabled=this.disabled||this.hasAttribute("disabled"),t.title=this.getAttribute("title-text")||this.titleText||i,t.setAttribute("aria-label",this.getAttribute("aria-text")||this.ariaText||i)}renderIcon(){return this.icon==="mark"?y`
        <svg viewBox="0 0 128 128" aria-hidden="true">
          ${Array.from({length:10},(t,i)=>y`
            <path
              d="M58 12 69 6l9 38-12 9-9-7z"
              transform="rotate(${i*36} 64 64)"
              fill=${i%2===0?"#FFFFFF":"#67E8F9"}
            ></path>
          `)}
          <circle cx="64" cy="64" r="14" fill="#FFFFFF"></circle>
        </svg>
      `:this.icon==="archive"?y`
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M5 3h11l3 3v15H5zM8 3v6h8V3M8 14h8M8 18h6"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linejoin="round"
          ></path>
        </svg>
      `:this.icon==="camera"?y`
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M14.5 4 16 7h3a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h3l1.5-3z"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linejoin="round"
          ></path>
          <circle
            cx="12"
            cy="13"
            r="3"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          ></circle>
        </svg>
      `:m}};w.styles=E`
    ${T(S)}

    :host {
      display: inline-flex;
      --sx-action-bg: var(--accent, #2563eb);
      --sx-action-border: var(--accent-strong, #1d4ed8);
      --sx-action-hover: var(--accent-strong, #1d4ed8);
      --sx-action-hover-border: #1e40af;
    }

    :host([variant="archive"]) {
      --sx-action-bg: #0891b2;
      --sx-action-border: #0e7490;
      --sx-action-hover: #0e7490;
      --sx-action-hover-border: #155e75;
    }

    :host([variant="capture"]) {
      --sx-action-bg: var(--text, #0f172a);
      --sx-action-border: #334155;
      --sx-action-hover: #334155;
      --sx-action-hover-border: #475569;
    }

    :host([state="saving"]),
    :host([state="archiving"]),
    :host([state="capturing"]) {
      --sx-action-bg: #475569;
      --sx-action-border: #334155;
      --sx-action-hover: #475569;
      --sx-action-hover-border: #334155;
    }

    :host([state="saved"]),
    :host([state="archived"]),
    :host([state="captured"]) {
      --sx-action-bg: var(--success, #16a34a);
      --sx-action-border: #047857;
      --sx-action-hover: #047857;
      --sx-action-hover-border: #065f46;
    }

    :host([state="error"]) {
      --sx-action-bg: var(--danger, #dc2626);
      --sx-action-border: #b91c1c;
      --sx-action-hover: #b91c1c;
      --sx-action-hover-border: #991b1b;
    }

    button {
      all: initial;
      box-sizing: border-box;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      height: 42px;
      min-width: 42px;
      padding: 0 14px 0 11px;
      border: 1px solid var(--sx-action-border);
      border-radius: var(--radius-sm, 6px);
      background: var(--sx-action-bg);
      color: #ffffff;
      box-shadow: var(--shadow-soft, 0 8px 22px rgba(15, 23, 42, 0.18));
      cursor: pointer;
      font: 700 14px/1 system-ui, Arial, sans-serif;
      white-space: nowrap;
      transition:
        background-color 140ms ease,
        border-color 140ms ease,
        box-shadow 140ms ease,
        transform 140ms ease;
    }

    :host([icon-only]) button {
      width: 42px;
      padding: 0;
    }

    :host([icon-only]) [data-label] {
      display: none;
    }

    button:hover:not(:disabled) {
      background: var(--sx-action-hover);
      border-color: var(--sx-action-hover-border);
      box-shadow: 0 12px 30px rgba(15, 23, 42, 0.34);
      transform: translateY(-1px);
    }

    button:focus-visible {
      outline: 3px solid rgba(6, 182, 212, 0.55);
      outline-offset: 2px;
    }

    button:disabled {
      cursor: wait;
    }

    svg {
      display: block;
      width: 20px;
      height: 20px;
      flex: 0 0 20px;
    }
  `,c([d({reflect:!0})],w.prototype,"variant",2),c([d({reflect:!0})],w.prototype,"state",2),c([d()],w.prototype,"label",2),c([d({attribute:"title-text"})],w.prototype,"titleText",2),c([d({attribute:"aria-text"})],w.prototype,"ariaText",2),c([d({reflect:!0})],w.prototype,"icon",2),c([d({type:Boolean,attribute:"icon-only",reflect:!0})],w.prototype,"iconOnly",2),c([d({type:Boolean,reflect:!0})],w.prototype,"disabled",2),w=c([$("sx-overlay-action")],w);var Bt="synthesix:external-overlay-position",C=16,qt=200,zt=170,L=class extends f{constructor(){super(...arguments);this.collapsed=!1;this.horizontalEdge="right";this.verticalEdge="bottom";this.dragState=null;this.handleResize=()=>{let t=this.getBoundingClientRect();if(!this.hasInlinePosition()){this.updateEdges(t.left,t.top,t.width,t.height);return}this.applyPosition(t.left,t.top,!1)};this.startDrag=t=>{if(t.button!==0)return;t.preventDefault(),t.stopPropagation();let i=this.getBoundingClientRect();t.currentTarget?.setPointerCapture?.(t.pointerId),this.dragState={height:i.height,pointerId:t.pointerId,startLeft:i.left,startTop:i.top,startX:t.clientX,startY:t.clientY,width:i.width},this.style.left=`${i.left}px`,this.style.top=`${i.top}px`,this.style.right="auto",this.style.bottom="auto",this.toggleAttribute("dragging",!0),window.addEventListener("pointermove",this.handleDragMove),window.addEventListener("pointerup",this.handleDragEnd),window.addEventListener("pointercancel",this.handleDragEnd)};this.handleDragMove=t=>{if(!this.dragState||t.pointerId!==this.dragState.pointerId)return;let i=this.dragState.startLeft+t.clientX-this.dragState.startX,s=this.dragState.startTop+t.clientY-this.dragState.startY;this.applyPosition(i,s,!1)};this.handleDragEnd=t=>{this.dragState&&t.pointerId!==this.dragState.pointerId||(this.persistPosition(),this.stopDrag())}}connectedCallback(){super.connectedCallback(),window.addEventListener("resize",this.handleResize)}disconnectedCallback(){window.removeEventListener("resize",this.handleResize),this.stopDrag(),super.disconnectedCallback()}firstUpdated(){this.restorePosition()}setCollapsed(t){if(this.collapsed===t)return;let i=this.getBoundingClientRect(),s=i.right,r=i.bottom,o=this.horizontalEdge,l=this.verticalEdge;this.collapsed=t,this.dispatchEvent(new CustomEvent("synthesix-overlay-toggle",{detail:{collapsed:this.collapsed},bubbles:!0,composed:!0})),this.updateComplete.then(()=>{let a=this.getBoundingClientRect(),p=o==="right"?s-a.width:i.left,u=l==="bottom"?r-a.height:i.top;this.applyPosition(p,u,!0)})}hasInlinePosition(){return this.style.left!==""&&this.style.top!==""}restorePosition(){try{let t=window.localStorage.getItem(Bt);if(!t){let s=this.getBoundingClientRect();this.updateEdges(s.left,s.top,s.width,s.height);return}let i=JSON.parse(t);if(typeof i.left!="number"||typeof i.top!="number")return;this.applyPosition(i.left,i.top,!1)}catch{let i=this.getBoundingClientRect();this.updateEdges(i.left,i.top,i.width,i.height)}}stopDrag(){this.dragState=null,this.toggleAttribute("dragging",!1),window.removeEventListener("pointermove",this.handleDragMove),window.removeEventListener("pointerup",this.handleDragEnd),window.removeEventListener("pointercancel",this.handleDragEnd)}applyPosition(t,i,s){let r=this.getBoundingClientRect(),o=r.width||this.dragState?.width||42,l=r.height||this.dragState?.height||36,a=this.clampPosition(t,i,o,l);this.style.left=`${a.left}px`,this.style.top=`${a.top}px`,this.style.right="auto",this.style.bottom="auto",this.updateEdges(a.left,a.top,o,l),s&&this.persistPosition()}clampPosition(t,i,s,r){let o=window.innerWidth||document.documentElement.clientWidth||s,l=window.innerHeight||document.documentElement.clientHeight||r,a=Math.max(C,o-s-C),p=Math.max(C,l-r-C);return{left:Math.min(Math.max(C,t),a),top:Math.min(Math.max(C,i),p)}}updateEdges(t,i,s,r){let o=window.innerWidth||document.documentElement.clientWidth||s,l=window.innerHeight||document.documentElement.clientHeight||r,a=o-t,p=t+s,u=l-i,h=i+r,_=t+s/2<o/2?"left":"right",v=i+r/2<l/2?"top":"bottom",N=a>=qt+C?"left":p>=qt+C?"right":a>=p?"left":"right",Wt=u>=zt+C?"top":h>=zt+C?"bottom":u>=h?"top":"bottom";this.horizontalEdge=_,this.verticalEdge=v,this.setAttribute("edge",_),this.setAttribute("vertical-edge",v),this.setAttribute("menu-edge",N),this.setAttribute("menu-vertical-edge",Wt)}persistPosition(){let t=this.getBoundingClientRect();try{window.localStorage.setItem(Bt,JSON.stringify({left:Math.round(t.left),top:Math.round(t.top)}))}catch{}}action(t){return this.querySelector(t)}setActionState(t,i,s,r){t&&(t.dataset.state=i,t.state=i,t.setAttribute("state",i),t.label=s,t.setAttribute("label",s),t.title=s,t.titleText=s,t.setAttribute("title-text",s),t.ariaText=s,t.setAttribute("aria-text",s),t.disabled=i===r,t.toggleAttribute("disabled",i===r))}setSaveButtonState(t,i){let s=this.action("[data-synthesix-save-page]");s&&(s.dataset.state=t,s.state=t,s.setAttribute("state",t),s.label=i,s.setAttribute("label",i),s.disabled=t==="saving",s.toggleAttribute("disabled",t==="saving"),s.titleText=s.title||i,s.setAttribute("title-text",s.title||i),s.ariaText=s.title||"Save page to active Synthesix investigation",s.setAttribute("aria-text",s.ariaText))}setCaptureState(t,i="Capture screenshot"){this.setActionState(this.action("[data-synthesix-capture]"),t,i,"capturing")}setArchiveState(t,i="Save page with HTML archive"){this.setActionState(this.action("[data-synthesix-archive]"),t,i,"archiving")}render(){return y`
      <div class="toolbar" data-synthesix-overlay-toolbar>
        <button
          class="grip"
          type="button"
          title="Drag Synthesix overlay"
          aria-label="Drag Synthesix overlay"
          data-synthesix-overlay-drag-handle
          @pointerdown=${this.startDrag}
        ></button>
        <slot name="toolbar"></slot>
        <button
          class="toggle"
          type="button"
          title="Collapse Synthesix overlay"
          aria-label="Collapse Synthesix overlay"
          data-synthesix-overlay-collapse
          @click=${()=>this.setCollapsed(!0)}
        >
          ${this.horizontalEdge==="left"?y`&lsaquo;`:y`&rsaquo;`}
        </button>
      </div>
      <div class="collapsed" data-synthesix-overlay-collapsed>
        <button
          class="grip"
          type="button"
          title="Drag Synthesix overlay"
          aria-label="Drag Synthesix overlay"
          data-synthesix-overlay-drag-handle
          @pointerdown=${this.startDrag}
        ></button>
        <button
          class="collapsed-toggle"
          type="button"
          title="Expand Synthesix overlay"
          aria-label="Expand Synthesix overlay"
          data-synthesix-overlay-expand
          @click=${()=>this.setCollapsed(!1)}
        >
          SX
        </button>
      </div>
      <slot></slot>
    `}};L.styles=E`
    ${T(S)}

    :host {
      all: initial;
      box-sizing: border-box;
      position: fixed;
      right: 18px;
      bottom: 18px;
      z-index: 2147483647;
      display: block;
      color: var(--text, #0f172a);
      font: 13px/1.2 system-ui, Arial, sans-serif;
      pointer-events: auto;
    }

    .toolbar {
      all: initial;
      box-sizing: border-box;
      display: flex;
      align-items: center;
      gap: 8px;
      pointer-events: auto;
      transform-origin: right bottom;
      transition:
        opacity 130ms ease,
        transform 130ms ease,
        filter 130ms ease;
    }

    :host([edge="left"]) .toolbar .grip {
      order: 10;
    }

    .grip {
      all: initial;
      box-sizing: border-box;
      display: inline-grid;
      width: 16px;
      height: 32px;
      place-items: center;
      border-radius: 999px;
      color: rgba(226, 232, 240, 0.95);
      cursor: grab;
      pointer-events: auto;
      touch-action: none;
      user-select: none;
    }

    .grip::before {
      content: "";
      display: block;
      width: 8px;
      height: 18px;
      background:
        radial-gradient(currentColor 1.4px, transparent 1.7px) 0 0 / 4px 6px;
      opacity: 0.9;
    }

    .grip:hover,
    .grip:focus-visible {
      background: rgba(15, 23, 42, 0.28);
      outline: none;
    }

    :host([dragging]) .grip {
      cursor: grabbing;
    }

    .toggle,
    .collapsed-toggle {
      all: initial;
      box-sizing: border-box;
      display: inline-grid;
      place-items: center;
      border: 1px solid rgba(148, 163, 184, 0.55);
      border-radius: 999px;
      background: rgba(15, 23, 42, 0.92);
      color: #f8fafc;
      box-shadow: 0 10px 26px rgba(15, 23, 42, 0.26);
      cursor: pointer;
      font: 800 12px/1 system-ui, Arial, sans-serif;
      user-select: none;
    }

    .toggle {
      width: 32px;
      height: 32px;
    }

    .collapsed-toggle {
      width: 42px;
      height: 36px;
      letter-spacing: 0;
    }

    .toggle:hover,
    .toggle:focus-visible,
    .collapsed-toggle:hover,
    .collapsed-toggle:focus-visible {
      border-color: var(--accent, #2563eb);
      background: var(--accent-strong, #1d4ed8);
      outline: none;
    }

    .collapsed {
      display: none;
      pointer-events: auto;
    }

    :host([collapsed]) .toolbar {
      position: absolute;
      right: 0;
      bottom: 0;
      opacity: 0;
      pointer-events: none;
      transform: translateX(10px) scale(0.92);
      filter: blur(1px);
    }

    :host([collapsed]) .collapsed {
      display: flex;
      align-items: center;
      flex-direction: column;
      gap: 6px;
      justify-content: flex-end;
      animation: sx-overlay-pop 140ms ease-out both;
    }

    :host([collapsed][vertical-edge="top"]) .collapsed {
      flex-direction: column-reverse;
    }

    :host([collapsed][edge="left"]) .collapsed {
      align-items: flex-start;
    }

    :host([collapsed][edge="right"]) .collapsed {
      align-items: flex-end;
    }

    :host([collapsed]) .grip {
      width: 42px;
      height: 36px;
      background: rgba(15, 23, 42, 0.92);
      border: 1px solid rgba(148, 163, 184, 0.45);
      box-shadow: 0 10px 26px rgba(15, 23, 42, 0.2);
    }

    :host([collapsed]) ::slotted(sx-overlay-capture-menu) {
      display: none !important;
    }

    :host([menu-edge="left"]) ::slotted(sx-overlay-capture-menu) {
      right: auto !important;
      left: 0 !important;
    }

    :host([menu-edge="right"]) ::slotted(sx-overlay-capture-menu) {
      right: 0 !important;
      left: auto !important;
    }

    :host([menu-vertical-edge="top"]) ::slotted(sx-overlay-capture-menu) {
      top: 50px !important;
      bottom: auto !important;
    }

    :host([menu-vertical-edge="bottom"]) ::slotted(sx-overlay-capture-menu) {
      top: auto !important;
      bottom: 50px !important;
    }

    @keyframes sx-overlay-pop {
      from {
        opacity: 0;
        transform: translateX(8px) scale(0.82);
      }
      to {
        opacity: 1;
        transform: translateX(0) scale(1);
      }
    }
  `,c([d({type:Boolean,reflect:!0})],L.prototype,"collapsed",2),c([x()],L.prototype,"horizontalEdge",2),c([x()],L.prototype,"verticalEdge",2),L=c([$("sx-overlay-root")],L);window.SynthesixOverlay={tokensCss:S,version:"0.1.0"};var he=n=>{let t=n.composedPath()[0]?.tagName;return t!=="INPUT"&&t!=="TEXTAREA"&&t!=="SELECT"?!1:n.composedPath().some(i=>{let s=i?.tagName;return typeof s=="string"&&s.startsWith("SX-OVERLAY-")})};for(let n of["keydown","keypress","keyup"])window.addEventListener(n,e=>{he(e)&&(e.stopImmediatePropagation(),e.stopPropagation())},!0);var ot="__synthesix-save-overlay",Kt="__synthesix-evidence-selection",Ft="synthesix:external-overlay-collapsed",ue="synthesix-overlay-main",ge="synthesix-extension-content",Vt=document.currentScript,J=Vt?.dataset.synthesixToken||"",Yt=Vt?.dataset.synthesixVersion||"0.1.0",Et=new Map,ye=0,xt={};function me(){return window.location.origin&&window.location.origin!=="null"?window.location.origin:"*"}J&&(document.documentElement.dataset.synthesixOverlayToken=J);function H(n){return typeof n=="object"&&n!==null}function rt(n){return typeof n=="string"?n:""}function G(n){return Array.isArray(n)?n.map(String).filter(e=>e.trim()):[]}function fe(n){return H(n)?Object.fromEntries(Object.entries(n).map(([e,t])=>[e,G(t)])):{}}function be(n){return H(n)?Object.fromEntries(Object.entries(n).map(([e,t])=>[e,H(t)?Object.fromEntries(Object.entries(t).map(([i,s])=>[i,String(s||"")])):{}])):{}}function ve(n){return H(n)?{baseTagsets:G(n.baseTagsets),id:rt(n.id),title:rt(n.title),existingTags:G(n.existingTags),graphEntities:Array.isArray(n.graphEntities)?n.graphEntities.filter(H).map(e=>({id:rt(e.id),label:rt(e.label),tags:G(e.tags),propertyKeys:G(e.propertyKeys)})).filter(e=>e.id.trim()):[],tagsetProperties:fe(n.tagsetProperties),tagsetPropertyTypes:be(n.tagsetPropertyTypes)}:{}}function xe(){let n=document.querySelector('meta[name="description" i]');return{url:window.location.href,title:document.title||window.location.hostname,description:n?.content||"",referrer:document.referrer||"",browserContext:{viewportWidth:window.innerWidth,viewportHeight:window.innerHeight,devicePixelRatio:window.devicePixelRatio||1,language:navigator.language||"",userAgent:navigator.userAgent||""}}}function A(n){let e=`overlay-${Date.now()}-${ye+=1}`;return Et.set(e,{action:n.action}),window.postMessage({source:ue,token:J,type:"synthesix:overlay-action",id:e,sourceToken:J,action:n},me()),e}function _e(n,e){e.variant&&(n.variant=e.variant,n.setAttribute("variant",e.variant)),e.icon&&(n.icon=e.icon,n.setAttribute("icon",e.icon)),e.iconOnly&&(n.iconOnly=!0,n.setAttribute("icon-only","")),e.label&&(n.label=e.label,n.setAttribute("label",e.label),n.textContent=e.label),e.ariaText&&(n.ariaText=e.ariaText,n.setAttribute("aria-text",e.ariaText)),e.titleText&&(n.titleText=e.titleText,n.setAttribute("title-text",e.titleText))}function _t(n,e){let t=document.createElement("sx-overlay-action");return t.setAttribute(n,""),t.setAttribute("slot","toolbar"),_e(t,e),t}function jt(){let n=new Date,e=t=>String(t).padStart(2,"0");return`screenshot_${n.getFullYear()}-${e(n.getMonth()+1)}-${e(n.getDate())}_${e(n.getHours())}-${e(n.getMinutes())}-${e(n.getSeconds())}`}function Ee(n){try{n.collapsed=window.localStorage.getItem(Ft)==="1",n.toggleAttribute("collapsed",n.collapsed)}catch{n.collapsed=!1}}function Q(n,e){n.title=e,n.titleText=e,n.setAttribute("title-text",e)}function at(n=xt){xt=ve(n);let e=document.getElementById(ot);if(e&&!e.hasAttribute("data-synthesix-extension-overlay"))return null;let t=e;if(!t){t=document.createElement("sx-overlay-root"),t.id=ot,t.setAttribute("data-synthesix-overlay-root",""),t.setAttribute("data-synthesix-extension-overlay",Yt),Ee(t);let i=_t("data-synthesix-save-page",{ariaText:"Save page to active Synthesix investigation",icon:"mark",label:"Save page",variant:"primary"});t.__synthesixSaveButton=i,t.__synthesixPagePayload=xe,t.__synthesixSetButtonState=(a,p)=>{t?.setSaveButtonState(a,p)},i.addEventListener("click",()=>{if(!t?.dataset.investigationId){A({action:"focus_home"});return}i.dataset.state!=="saved"&&(t.__synthesixSetButtonState?.("saving","Saving..."),A({action:"save_page_to_investigation",investigationId:t.dataset.investigationId,page:t.__synthesixPagePayload?.()}))});let s=_t("data-synthesix-archive",{icon:"archive",iconOnly:!0,variant:"archive"});t.__synthesixArchiveButton=s,t.__synthesixSetArchiveState=(a,p="Save page with HTML archive")=>{t?.setArchiveState(a,p)},s.addEventListener("click",()=>{if(!t?.dataset.investigationId){A({action:"focus_home"});return}t.__synthesixSetArchiveState?.("archiving","Saving HTML archive..."),A({action:"archive_page_to_investigation",investigationId:t.dataset.investigationId,page:t.__synthesixPagePayload?.()})});let r=_t("data-synthesix-capture",{icon:"camera",iconOnly:!0,variant:"capture"});t.__synthesixCaptureButton=r;let o=document.createElement("sx-overlay-capture-menu");o.setAttribute("data-synthesix-capture-menu",""),o.tagsetProperties={},t.__synthesixDefaultCaptureName=jt,t.__synthesixSetCaptureState=(a,p="Capture screenshot")=>{t?.setCaptureState(a,p)},t.__synthesixQueueCapture=(a,p,u,h)=>{t?.__synthesixSetCaptureState?.("capturing","Capturing evidence..."),t&&(t.style.display="none"),window.requestAnimationFrame(()=>{window.requestAnimationFrame(()=>{A({action:"capture_evidence_to_investigation",investigationId:t?.dataset.investigationId,captureScope:a,captureName:String(u||"").trim(),selection:p,attach:h||null,page:t?.__synthesixPagePayload?.()}),o.reset?.()})})},t.__synthesixStartRegionSelection=(a,p)=>{if(!t)return;let u=t;u.style.display="none",document.getElementById(Kt)?.remove();let h=document.createElement("sx-overlay-selection-box");h.id=Kt,h.addEventListener("synthesix-region-selected",_=>{h.remove();let v=_.detail||{};t?.__synthesixQueueCapture?.("region",{x:v.x,y:v.y,width:v.width,height:v.height},a,p)}),h.addEventListener("synthesix-region-cancel",()=>{h.remove(),u.style.display="block"}),(document.documentElement||document.body).appendChild(h)},o.addEventListener("synthesix-capture-choice",a=>{let p=a.detail||{};if(!t?.dataset.investigationId){A({action:"focus_home"});return}p.scope==="viewport"?t.__synthesixQueueCapture?.("viewport",{x:window.scrollX,y:window.scrollY,width:window.innerWidth,height:window.innerHeight},p.captureName||"",p.attach||null):p.scope==="region"&&t.__synthesixStartRegionSelection?.(p.captureName||"",p.attach||null)}),r.addEventListener("click",()=>{if(!t?.dataset.investigationId){A({action:"focus_home"});return}let a=!o.hasAttribute("open");o.open=a,o.toggleAttribute("open",a),a&&o.ensureCaptureName?.(t.__synthesixDefaultCaptureName?.()||jt())});let l=document.createElement("sx-overlay-entity-menu");l.baseTagsets=[],l.tagsetProperties={},l.tagsetPropertyTypes={},t.__synthesixSetTagsetMetadata=a=>{l.baseTagsets=a.baseTagsets||[],l.tagsetProperties=a.tagsetProperties||{},l.tagsetPropertyTypes=a.tagsetPropertyTypes||{},o.tagsetProperties=a.tagsetProperties||{}},t.__synthesixSetEntityTagsets=a=>{l.existingTags=Array.isArray(a)?a:[]},t.__synthesixSetGraphEntities=a=>{let p=Array.isArray(a)?a:[];l.graphEntities=p,o.graphEntities=p},l.addEventListener("synthesix-entity-create",a=>{let p=a.detail||{};if(!t?.dataset.investigationId){A({action:"focus_home"});return}A({action:"create_graph_entity_from_selection",investigationId:t.dataset.investigationId,entity:{label:p.label,category:p.category},page:t.__synthesixPagePayload?.()})}),l.addEventListener("synthesix-entity-attach",a=>{let p=a.detail||{};if(!t?.dataset.investigationId){A({action:"focus_home"});return}A({action:"attach_selection_to_graph_entity",investigationId:t.dataset.investigationId,entityId:p.entityId,property:{key:p.propertyKey,value:p.label,property_type:p.propertyType||""},page:t.__synthesixPagePayload?.()})}),t.addEventListener("synthesix-overlay-toggle",a=>{let p=!!a.detail?.collapsed;try{window.localStorage.setItem(Ft,p?"1":"0")}catch{}p&&(o.reset?.(),o.open=!1,o.removeAttribute("open"))}),t.append(i,s,r,o,l),(document.documentElement||document.body).appendChild(t)}return we(t,xt),t}function we(n,e){let t=e.id||"",i=e.title||"",s=`${t}|${window.location.href}`,r=n.dataset.pageKey!==s;n.dataset.investigationId=t,n.dataset.pageKey=s,n.__synthesixSetTagsetMetadata?.(e),n.__synthesixSetGraphEntities?.(e.graphEntities||[]),n.__synthesixSetEntityTagsets?.(e.existingTags||[]);let o=n.__synthesixSaveButton||n.querySelector("[data-synthesix-save-page]");if(!o)return;let l=Number(n.dataset.statusUntil||0),a=Number(n.dataset.captureStatusUntil||0),p=Number(n.dataset.archiveStatusUntil||0);r?(n.dataset.saved="0",n.dataset.statusUntil="0",t?(Q(o,`Save this page to "${i}"`),n.__synthesixSetButtonState?.("idle","Save page")):(Q(o,"Open Synthesix to select an investigation before saving this page"),n.__synthesixSetButtonState?.("idle","Select investigation")),n.__synthesixSetCaptureState?.("idle","Capture screenshot"),n.__synthesixSetArchiveState?.("idle","Save page with HTML archive")):o.dataset.state==="error"&&Date.now()>=l&&(Q(o,t?`Save this page to "${i}"`:"Open Synthesix to select an investigation before saving this page"),n.__synthesixSetButtonState?.("idle","Save page"));let u=n.__synthesixCaptureButton||n.querySelector("[data-synthesix-capture]");["captured","error"].includes(u?.dataset.state||"")&&Date.now()>=a&&n.__synthesixSetCaptureState?.("idle","Capture screenshot");let h=n.__synthesixArchiveButton||n.querySelector("[data-synthesix-archive]");["archived","error"].includes(h?.dataset.state||"")&&Date.now()>=p&&n.__synthesixSetArchiveState?.("idle","Save page with HTML archive"),t&&n.dataset.observationKey!==s&&(n.dataset.observationKey=s,A({action:"observe_saved_page",investigationId:t,page:{url:window.location.href}}))}function $e(n){if(!H(n))return;let e=document.getElementById(ot);if(!e)return;let t=String(n.kind||""),i=String(n.state||""),s=String(n.message||""),r=i==="error";if(t==="save"){let o=e.__synthesixSaveButton||e.querySelector("[data-synthesix-save-page]");e.dataset.saved=r?"0":"1",o&&Q(o,s),e.__synthesixSetButtonState?.(r?"error":"saved",s),e.dataset.statusUntil=r?String(Date.now()+1800):"0"}else t==="capture"?(e.style.display="block",e.__synthesixSetCaptureState?.(r?"error":"captured",s),e.dataset.captureStatusUntil=String(Date.now()+2200)):t==="archive"&&(e.__synthesixSetArchiveState?.(r?"error":"archived",s),e.dataset.archiveStatusUntil=String(Date.now()+2200))}function Ae(n,e){let t=Et.get(n);if(!t)return;Et.delete(n);let i=document.getElementById(ot);if(!i)return;let s=H(e)?e:{},r=s.ok!==!1;if(s.backendBinding!==!0){if(!r){t.action==="capture_evidence_to_investigation"?(i.style.display="block",i.__synthesixSetCaptureState?.("error","Capture could not be queued"),i.dataset.captureStatusUntil=String(Date.now()+2200)):t.action==="archive_page_to_investigation"?(i.__synthesixSetArchiveState?.("error","Archive could not be queued"),i.dataset.archiveStatusUntil=String(Date.now()+2200)):t.action==="save_page_to_investigation"&&(i.__synthesixSetButtonState?.("error","Save could not be queued"),i.dataset.statusUntil=String(Date.now()+1800));return}if(t.action==="capture_evidence_to_investigation")i.style.display="block",i.__synthesixSetCaptureState?.("captured","Capture queued in extension"),i.dataset.captureStatusUntil=String(Date.now()+2200);else if(t.action==="archive_page_to_investigation")i.__synthesixSetArchiveState?.("archived","Archive queued in extension"),i.dataset.archiveStatusUntil=String(Date.now()+2200);else if(t.action==="save_page_to_investigation"){let l=i.__synthesixSaveButton;i.dataset.saved="1",l&&Q(l,"Save queued in extension"),i.__synthesixSetButtonState?.("saved","Queued")}}}window.addEventListener("message",n=>{let e=n.data;!H(e)||e.source!==ge||e.token!==J||(e.type==="synthesix:install-overlay"||e.type==="synthesix:context-update"?at(e.context):e.type==="synthesix:button-status"?$e(e.status):e.type==="synthesix:overlay-ack"&&typeof e.id=="string"&&Ae(e.id,e.response))});window.SynthesixExtensionOverlay={install:at,version:Yt};at({});})();
