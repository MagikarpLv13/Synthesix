"use strict";(()=>{var Rt=Object.defineProperty;var Mt=Object.getOwnPropertyDescriptor;var a=(o,e,t,i)=>{for(var s=i>1?void 0:i?Mt(e,t):e,r=o.length-1,n;r>=0;r--)(n=o[r])&&(s=(i?n(e,t,s):n(s))||s);return i&&s&&Rt(e,t,s),s};var A=`
:host {
  --accent: #2A46A6;
  --accent-strong: #23408F;
  --accent-soft: #E4E8F6;
  --accent-ink: #17225A;
  --accent-on-dark: #8AA0EE;
  --surface: #FBF9F4;
  --surface-2: #FCFBF8;
  --surface-sunken: #ECE8DE;
  --text: #191A1E;
  --text-muted: #56513F;
  --muted: #56513F;
  --line: #DAD4C7;
  --ink-surface: #17181D;
  --ink-surface-2: #1F2027;
  --ink-border: #2B2D34;
  --on-ink: #EDEAE2;
  --on-ink-strong: #F7F5EF;
  --success: #28613C;
  --success-soft: #E1EEE3;
  --success-ink: #1E4B2E;
  --danger: #B33A3A;
  --font-ui: "Public Sans", system-ui, Arial, sans-serif;
  --font-mono: "IBM Plex Mono", Consolas, monospace;
  --radius-sm: 7px;
  --radius-md: 8px;
  --shadow-soft: 0 10px 26px rgba(23, 24, 30, 0.22);
}
`;var W=globalThis,G=W.ShadowRoot&&(W.ShadyCSS===void 0||W.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,tt=Symbol(),ht=new WeakMap,q=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==tt)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(G&&e===void 0){let i=t!==void 0&&t.length===1;i&&(e=ht.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&ht.set(t,e))}return e}toString(){return this.cssText}},k=o=>new q(typeof o=="string"?o:o+"",void 0,tt),x=(o,...e)=>{let t=o.length===1?o[0]:e.reduce((i,s,r)=>i+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+o[r+1],o[0]);return new q(t,o,tt)},ut=(o,e)=>{if(G)o.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let i=document.createElement("style"),s=W.litNonce;s!==void 0&&i.setAttribute("nonce",s),i.textContent=t.cssText,o.appendChild(i)}},et=G?o=>o:o=>o instanceof CSSStyleSheet?(e=>{let t="";for(let i of e.cssRules)t+=i.cssText;return k(t)})(o):o;var{is:Dt,defineProperty:It,getOwnPropertyDescriptor:Nt,getOwnPropertyNames:Ut,getOwnPropertySymbols:zt,getPrototypeOf:qt}=Object,O=globalThis,gt=O.trustedTypes,jt=gt?gt.emptyScript:"",Kt=O.reactiveElementPolyfillSupport,j=(o,e)=>o,K={toAttribute(o,e){switch(e){case Boolean:o=o?jt:null;break;case Object:case Array:o=o==null?o:JSON.stringify(o)}return o},fromAttribute(o,e){let t=o;switch(e){case Boolean:t=o!==null;break;case Number:t=o===null?null:Number(o);break;case Object:case Array:try{t=JSON.parse(o)}catch{t=null}}return t}},J=(o,e)=>!Dt(o,e),mt={attribute:!0,type:String,converter:K,reflect:!1,useDefault:!1,hasChanged:J};Symbol.metadata??=Symbol("metadata"),O.litPropertyMetadata??=new WeakMap;var T=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=mt){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let i=Symbol(),s=this.getPropertyDescriptor(e,i,t);s!==void 0&&It(this.prototype,e,s)}}static getPropertyDescriptor(e,t,i){let{get:s,set:r}=Nt(this.prototype,e)??{get(){return this[t]},set(n){this[t]=n}};return{get:s,set(n){let c=s?.call(this);r?.call(this,n),this.requestUpdate(e,c,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??mt}static _$Ei(){if(this.hasOwnProperty(j("elementProperties")))return;let e=qt(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(j("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(j("properties"))){let t=this.properties,i=[...Ut(t),...zt(t)];for(let s of i)this.createProperty(s,t[s])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[i,s]of t)this.elementProperties.set(i,s)}this._$Eh=new Map;for(let[t,i]of this.elementProperties){let s=this._$Eu(t,i);s!==void 0&&this._$Eh.set(s,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let i=new Set(e.flat(1/0).reverse());for(let s of i)t.unshift(et(s))}else e!==void 0&&t.push(et(e));return t}static _$Eu(e,t){let i=t.attribute;return i===!1?void 0:typeof i=="string"?i:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return ut(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){let i=this.constructor.elementProperties.get(e),s=this.constructor._$Eu(e,i);if(s!==void 0&&i.reflect===!0){let r=(i.converter?.toAttribute!==void 0?i.converter:K).toAttribute(t,i.type);this._$Em=e,r==null?this.removeAttribute(s):this.setAttribute(s,r),this._$Em=null}}_$AK(e,t){let i=this.constructor,s=i._$Eh.get(e);if(s!==void 0&&this._$Em!==s){let r=i.getPropertyOptions(s),n=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:K;this._$Em=s;let c=n.fromAttribute(t,r.type);this[s]=c??this._$Ej?.get(s)??c,this._$Em=null}}requestUpdate(e,t,i,s=!1,r){if(e!==void 0){let n=this.constructor;if(s===!1&&(r=this[e]),i??=n.getPropertyOptions(e),!((i.hasChanged??J)(r,t)||i.useDefault&&i.reflect&&r===this._$Ej?.get(e)&&!this.hasAttribute(n._$Eu(e,i))))return;this.C(e,t,i)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:s,wrapped:r},n){i&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,n??t??this[e]),r!==!0||n!==void 0)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),s===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[s,r]of this._$Ep)this[s]=r;this._$Ep=void 0}let i=this.constructor.elementProperties;if(i.size>0)for(let[s,r]of i){let{wrapped:n}=r,c=this[s];n!==!0||this._$AL.has(s)||c===void 0||this.C(s,void 0,r,c)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(i=>i.hostUpdate?.()),this.update(t)):this._$EM()}catch(i){throw e=!1,this._$EM(),i}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};T.elementStyles=[],T.shadowRootOptions={mode:"open"},T[j("elementProperties")]=new Map,T[j("finalized")]=new Map,Kt?.({ReactiveElement:T}),(O.reactiveElementVersions??=[]).push("2.1.2");var lt=globalThis,ft=o=>o,Z=lt.trustedTypes,bt=Z?Z.createPolicy("lit-html",{createHTML:o=>o}):void 0,$t="$lit$",S=`lit$${Math.random().toFixed(9).slice(2)}$`,wt="?"+S,Vt=`<${wt}>`,R=document,B=()=>R.createComment(""),X=o=>o===null||typeof o!="object"&&typeof o!="function",ct=Array.isArray,Bt=o=>ct(o)||typeof o?.[Symbol.iterator]=="function",it=`[ 	
\f\r]`,V=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,yt=/-->/g,vt=/>/g,L=RegExp(`>|${it}(?:([^\\s"'>=/]+)(${it}*=${it}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),xt=/'/g,_t=/"/g,At=/^(?:script|style|textarea|title)$/i,pt=o=>(e,...t)=>({_$litType$:o,strings:e,values:t}),g=pt(1),se=pt(2),re=pt(3),M=Symbol.for("lit-noChange"),f=Symbol.for("lit-nothing"),Et=new WeakMap,H=R.createTreeWalker(R,129);function kt(o,e){if(!ct(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return bt!==void 0?bt.createHTML(e):e}var Xt=(o,e)=>{let t=o.length-1,i=[],s,r=e===2?"<svg>":e===3?"<math>":"",n=V;for(let c=0;c<t;c++){let l=o[c],u,m,d=-1,E=0;for(;E<l.length&&(n.lastIndex=E,m=n.exec(l),m!==null);)E=n.lastIndex,n===V?m[1]==="!--"?n=yt:m[1]!==void 0?n=vt:m[2]!==void 0?(At.test(m[2])&&(s=RegExp("</"+m[2],"g")),n=L):m[3]!==void 0&&(n=L):n===L?m[0]===">"?(n=s??V,d=-1):m[1]===void 0?d=-2:(d=n.lastIndex-m[2].length,u=m[1],n=m[3]===void 0?L:m[3]==='"'?_t:xt):n===_t||n===xt?n=L:n===yt||n===vt?n=V:(n=L,s=void 0);let w=n===L&&o[c+1].startsWith("/>")?" ":"";r+=n===V?l+Vt:d>=0?(i.push(u),l.slice(0,d)+$t+l.slice(d)+S+w):l+S+(d===-2?c:w)}return[kt(o,r+(o[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),i]},Y=class o{constructor({strings:e,_$litType$:t},i){let s;this.parts=[];let r=0,n=0,c=e.length-1,l=this.parts,[u,m]=Xt(e,t);if(this.el=o.createElement(u,i),H.currentNode=this.el.content,t===2||t===3){let d=this.el.content.firstChild;d.replaceWith(...d.childNodes)}for(;(s=H.nextNode())!==null&&l.length<c;){if(s.nodeType===1){if(s.hasAttributes())for(let d of s.getAttributeNames())if(d.endsWith($t)){let E=m[n++],w=s.getAttribute(d).split(S),D=/([.?@])?(.*)/.exec(E);l.push({type:1,index:r,name:D[2],strings:w,ctor:D[1]==="."?rt:D[1]==="?"?ot:D[1]==="@"?nt:N}),s.removeAttribute(d)}else d.startsWith(S)&&(l.push({type:6,index:r}),s.removeAttribute(d));if(At.test(s.tagName)){let d=s.textContent.split(S),E=d.length-1;if(E>0){s.textContent=Z?Z.emptyScript:"";for(let w=0;w<E;w++)s.append(d[w],B()),H.nextNode(),l.push({type:2,index:++r});s.append(d[E],B())}}}else if(s.nodeType===8)if(s.data===wt)l.push({type:2,index:r});else{let d=-1;for(;(d=s.data.indexOf(S,d+1))!==-1;)l.push({type:7,index:r}),d+=S.length-1}r++}}static createElement(e,t){let i=R.createElement("template");return i.innerHTML=e,i}};function I(o,e,t=o,i){if(e===M)return e;let s=i!==void 0?t._$Co?.[i]:t._$Cl,r=X(e)?void 0:e._$litDirective$;return s?.constructor!==r&&(s?._$AO?.(!1),r===void 0?s=void 0:(s=new r(o),s._$AT(o,t,i)),i!==void 0?(t._$Co??=[])[i]=s:t._$Cl=s),s!==void 0&&(e=I(o,s._$AS(o,e.values),s,i)),e}var st=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:i}=this._$AD,s=(e?.creationScope??R).importNode(t,!0);H.currentNode=s;let r=H.nextNode(),n=0,c=0,l=i[0];for(;l!==void 0;){if(n===l.index){let u;l.type===2?u=new F(r,r.nextSibling,this,e):l.type===1?u=new l.ctor(r,l.name,l.strings,this,e):l.type===6&&(u=new at(r,this,e)),this._$AV.push(u),l=i[++c]}n!==l?.index&&(r=H.nextNode(),n++)}return H.currentNode=R,s}p(e){let t=0;for(let i of this._$AV)i!==void 0&&(i.strings!==void 0?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}},F=class o{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,s){this.type=2,this._$AH=f,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=I(this,e,t),X(e)?e===f||e==null||e===""?(this._$AH!==f&&this._$AR(),this._$AH=f):e!==this._$AH&&e!==M&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Bt(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==f&&X(this._$AH)?this._$AA.nextSibling.data=e:this.T(R.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:i}=e,s=typeof i=="number"?this._$AC(e):(i.el===void 0&&(i.el=Y.createElement(kt(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(t);else{let r=new st(s,this),n=r.u(this.options);r.p(t),this.T(n),this._$AH=r}}_$AC(e){let t=Et.get(e.strings);return t===void 0&&Et.set(e.strings,t=new Y(e)),t}k(e){ct(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,i,s=0;for(let r of e)s===t.length?t.push(i=new o(this.O(B()),this.O(B()),this,this.options)):i=t[s],i._$AI(r),s++;s<t.length&&(this._$AR(i&&i._$AB.nextSibling,s),t.length=s)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let i=ft(e).nextSibling;ft(e).remove(),e=i}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},N=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,s,r){this.type=1,this._$AH=f,this._$AN=void 0,this.element=e,this.name=t,this._$AM=s,this.options=r,i.length>2||i[0]!==""||i[1]!==""?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=f}_$AI(e,t=this,i,s){let r=this.strings,n=!1;if(r===void 0)e=I(this,e,t,0),n=!X(e)||e!==this._$AH&&e!==M,n&&(this._$AH=e);else{let c=e,l,u;for(e=r[0],l=0;l<r.length-1;l++)u=I(this,c[i+l],t,l),u===M&&(u=this._$AH[l]),n||=!X(u)||u!==this._$AH[l],u===f?e=f:e!==f&&(e+=(u??"")+r[l+1]),this._$AH[l]=u}n&&!s&&this.j(e)}j(e){e===f?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},rt=class extends N{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===f?void 0:e}},ot=class extends N{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==f)}},nt=class extends N{constructor(e,t,i,s,r){super(e,t,i,s,r),this.type=5}_$AI(e,t=this){if((e=I(this,e,t,0)??f)===M)return;let i=this._$AH,s=e===f&&i!==f||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,r=e!==f&&(i===f||s);s&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},at=class{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){I(this,e)}};var Yt=lt.litHtmlPolyfillSupport;Yt?.(Y,F),(lt.litHtmlVersions??=[]).push("3.3.3");var Ct=(o,e,t)=>{let i=t?.renderBefore??e,s=i._$litPart$;if(s===void 0){let r=t?.renderBefore??null;i._$litPart$=s=new F(e.insertBefore(B(),r),r,void 0,t??{})}return s._$AI(o),s};var dt=globalThis,b=class extends T{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Ct(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return M}};b._$litElement$=!0,b.finalized=!0,dt.litElementHydrateSupport?.({LitElement:b});var Ft=dt.litElementPolyfillSupport;Ft?.({LitElement:b});(dt.litElementVersions??=[]).push("4.2.2");var $=o=>(e,t)=>{t!==void 0?t.addInitializer(()=>{customElements.define(o,e)}):customElements.define(o,e)};var Wt={attribute:!0,type:String,converter:K,reflect:!1,hasChanged:J},Gt=(o=Wt,e,t)=>{let{kind:i,metadata:s}=t,r=globalThis.litPropertyMetadata.get(s);if(r===void 0&&globalThis.litPropertyMetadata.set(s,r=new Map),i==="setter"&&((o=Object.create(o)).wrapped=!0),r.set(t.name,o),i==="accessor"){let{name:n}=t;return{set(c){let l=e.get.call(this);e.set.call(this,c),this.requestUpdate(n,l,o,!0,c)},init(c){return c!==void 0&&this.C(n,void 0,o,c),c}}}if(i==="setter"){let{name:n}=t;return function(c){let l=this[n];e.call(this,c),this.requestUpdate(n,l,o,!0,c)}}throw Error("Unsupported decorator location: "+i)};function p(o){return(e,t)=>typeof t=="object"?Gt(o,e,t):((i,s,r)=>{let n=s.hasOwnProperty(r);return s.constructor.createProperty(r,i),n?Object.getOwnPropertyDescriptor(s,r):void 0})(o,e,t)}function v(o){return p({...o,state:!0,attribute:!1})}var y=class extends b{constructor(){super(...arguments);this.open=!1;this.graphEntities=[];this.tagsetProperties={};this.placeholder="Capture name (optional)";this.nameLabel="Capture name";this.viewportLabel="Visible area";this.regionLabel="Select area";this.attachHeading="Attach to entity (optional)";this.chooseEntityLabel="Don't attach";this.propertyPlaceholder="Property name";this.defaultPropertyKey="Capture \xE9cran";this._selectedEntityId="";this._onEntityChange=t=>{this._selectedEntityId=t.target.value}}get captureName(){return this.input()?.value.trim()||""}set captureName(t){let i=this.input();i&&(i.value=t)}ensureCaptureName(t){let i=this.input();i&&!i.value.trim()&&(i.value=t)}reset(){this.captureName="",this._selectedEntityId="";let t=this.propertyInput();t&&(t.value="");let i=this.entitySelect();i&&(i.value=""),this.open=!1}get _entities(){return this.graphEntities.filter(t=>String(t.id??"").trim())}get _propertySuggestions(){let t=this._entities.find(n=>String(n.id??"").trim()===this._selectedEntityId.trim());if(!t)return[];let i=new Set,s=[],r=n=>{let c=String(n??"").trim(),l=c.toLowerCase();!c||i.has(l)||(i.add(l),s.push(c))};for(let n of t.tags??[])for(let c of this.tagsetProperties[String(n??"").trim()]??[])r(c);for(let n of t.propertyKeys??[])r(n);return s}get _attach(){if(!this._selectedEntityId)return null;let t=this.propertyInput()?.value.trim()||this.defaultPropertyKey;return{entityId:this._selectedEntityId,propertyKey:t,propertyType:""}}firstUpdated(){this.renderRoot.querySelectorAll("[data-scope]").forEach(t=>{t.addEventListener("click",()=>{this.choose(t.dataset.scope)})})}render(){let t=this._entities.length>0;return g`
      <input
        class="name-input"
        type="text"
        maxlength="120"
        placeholder=${this.placeholder}
        aria-label=${this.nameLabel}
      >
      ${t?g`
            <div class="attach">
              <div class="attach-heading">${this.attachHeading}</div>
              <select
                class="entity-select"
                aria-label=${this.attachHeading}
                @change=${this._onEntityChange}
              >
                <option value="">${this.chooseEntityLabel}</option>
                ${this._entities.map(i=>g`
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
                ${this._propertySuggestions.map(i=>g`<option value=${i}></option>`)}
              </datalist>
            </div>
          `:""}
      <button type="button" data-scope="viewport">${this.viewportLabel}</button>
      <button type="button" data-scope="region">${this.regionLabel}</button>
    `}input(){return this.renderRoot.querySelector(".name-input")}propertyInput(){return this.renderRoot.querySelector(".prop-input")}entitySelect(){return this.renderRoot.querySelector(".entity-select")}choose(t){this.open=!1,this.dispatchEvent(new CustomEvent("synthesix-capture-choice",{bubbles:!0,composed:!0,detail:{scope:t,captureName:this.captureName,attach:this._attach}}))}};y.styles=x`
    ${k(A)}

    :host {
      box-sizing: border-box;
      display: none;
      position: absolute;
      right: 0;
      bottom: 50px;
      width: 220px;
      padding: 6px;
      border: 1px solid var(--ink-border, #2b2d34);
      border-left: 3px solid var(--accent, #2a46a6);
      border-radius: var(--radius-sm, 7px);
      background: var(--ink-surface, #17181d);
      box-shadow: 0 18px 42px rgba(14, 15, 18, 0.4);
      color: var(--on-ink, #edeae2);
      font: 600 13px/1.25 var(--font-ui, system-ui, Arial, sans-serif);
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
      border: 1px solid var(--ink-border, #2b2d34);
      border-radius: var(--radius-sm, 7px);
      background: var(--ink-surface-2, #1f2027);
      color: var(--on-ink-strong, #f7f5ef);
      font: 500 13px/1.2 var(--font-ui, system-ui, Arial, sans-serif);
    }

    .attach {
      margin: 2px 0 6px;
      padding-top: 6px;
      border-top: 1px solid #262830;
    }

    .attach-heading {
      margin-bottom: 4px;
      color: var(--accent-on-dark, #8aa0ee);
      font: 600 11px/1.2 var(--font-mono, monospace);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    button {
      all: initial;
      box-sizing: border-box;
      display: block;
      width: 100%;
      padding: 9px 10px;
      border-radius: var(--radius-sm, 7px);
      color: var(--on-ink, #edeae2);
      cursor: pointer;
      font: 600 13px/1.2 var(--font-ui, system-ui, Arial, sans-serif);
    }

    button:hover,
    button:focus-visible {
      background: #2b2d34;
      color: var(--accent-on-dark, #8aa0ee);
      outline: none;
    }
  `,a([p({type:Boolean,reflect:!0})],y.prototype,"open",2),a([p({attribute:!1})],y.prototype,"graphEntities",2),a([p({attribute:!1})],y.prototype,"tagsetProperties",2),a([p()],y.prototype,"placeholder",2),a([p({attribute:"name-label"})],y.prototype,"nameLabel",2),a([p({attribute:"viewport-label"})],y.prototype,"viewportLabel",2),a([p({attribute:"region-label"})],y.prototype,"regionLabel",2),a([p({attribute:"attach-heading"})],y.prototype,"attachHeading",2),a([p({attribute:"choose-entity-label"})],y.prototype,"chooseEntityLabel",2),a([p({attribute:"property-placeholder"})],y.prototype,"propertyPlaceholder",2),a([p({attribute:"default-property-key"})],y.prototype,"defaultPropertyKey",2),a([v()],y.prototype,"_selectedEntityId",2),y=a([$("sx-overlay-capture-menu")],y);var U=class extends b{constructor(){super(...arguments);this.label=""}render(){return g`<button type="button"></button>`}updated(){let t=this.renderRoot.querySelector("button");if(!t)return;let i=this.getAttribute("label")||this.label;t.textContent=i,t.setAttribute("aria-label",i)}};U.styles=x`
    ${k(A)}

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
      border: 1px solid var(--accent-strong, #23408f);
      border-radius: 999px;
      background: var(--accent, #2a46a6);
      color: #ffffff;
      box-shadow: 0 10px 26px rgba(23, 24, 30, 0.26);
      cursor: pointer;
      font: 700 12px/1.1 var(--font-ui, system-ui, Arial, sans-serif);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    button:hover,
    button:focus-visible {
      background: var(--accent-strong, #23408f);
      outline: 3px solid rgba(138, 160, 238, 0.45);
      outline-offset: 2px;
    }
  `,a([p()],U.prototype,"label",2),U=a([$("sx-overlay-selection-trigger")],U);var z=class extends b{constructor(){super(...arguments);this.hint="Drag to select evidence \xB7 Esc to cancel";this._selecting=!1;this._startX=0;this._startY=0;this._onKeyDown=t=>{t.key==="Escape"&&(t.preventDefault(),this._emitCancel())};this._onPointerDown=t=>{t.preventDefault(),this._selecting=!0,this._startX=t.clientX,this._startY=t.clientY;let i=this._boxEl;i&&i.classList.add("is-active");try{this.setPointerCapture(t.pointerId)}catch{}};this._onPointerMove=t=>{if(!this._selecting)return;let i=this._boxEl;if(!i)return;let s=Math.min(this._startX,t.clientX),r=Math.min(this._startY,t.clientY);i.style.left=`${s}px`,i.style.top=`${r}px`,i.style.width=`${Math.abs(t.clientX-this._startX)}px`,i.style.height=`${Math.abs(t.clientY-this._startY)}px`};this._onPointerUp=t=>{if(!this._selecting)return;this._selecting=!1;let i=Math.min(this._startX,t.clientX),s=Math.min(this._startY,t.clientY),r=Math.abs(t.clientX-this._startX),n=Math.abs(t.clientY-this._startY);if(r<8||n<8){this._emitCancel();return}this.dispatchEvent(new CustomEvent("synthesix-region-selected",{bubbles:!0,composed:!0,detail:{x:i+window.scrollX,y:s+window.scrollY,width:r,height:n}}))}}connectedCallback(){super.connectedCallback(),document.addEventListener("keydown",this._onKeyDown,!0),this.addEventListener("pointerdown",this._onPointerDown),this.addEventListener("pointermove",this._onPointerMove),this.addEventListener("pointerup",this._onPointerUp)}disconnectedCallback(){document.removeEventListener("keydown",this._onKeyDown,!0),super.disconnectedCallback()}get _boxEl(){return this.renderRoot.querySelector(".box")}_emitCancel(){this.dispatchEvent(new CustomEvent("synthesix-region-cancel",{bubbles:!0,composed:!0}))}render(){return g`
      <div class="hint">${this.hint}</div>
      <div class="box"></div>
    `}};z.styles=x`
    :host {
      all: initial;
      display: block;
      position: fixed;
      inset: 0;
      z-index: 2147483647;
      cursor: crosshair;
      background: rgba(23, 24, 29, 0.16);
      user-select: none;
      touch-action: none;
    }
    .hint {
      position: fixed;
      top: 16px;
      left: 50%;
      transform: translateX(-50%);
      padding: 9px 12px;
      border-radius: 7px;
      background: #17181d;
      color: #f7f5ef;
      box-shadow: 0 8px 24px rgba(23, 24, 30, 0.3);
      font: 600 13px var(--font-ui, Arial, sans-serif);
      pointer-events: none;
    }
    .box {
      display: none;
      position: fixed;
      border: 2px solid #2a46a6;
      background: rgba(42, 70, 166, 0.12);
      box-shadow: 0 0 0 9999px rgba(23, 24, 29, 0.38);
      pointer-events: none;
    }
    .box.is-active {
      display: block;
    }
  `,a([p()],z.prototype,"hint",2),z=a([$("sx-overlay-selection-box")],z);var Tt={text:"Texte",number:"Nombre",date:"Date",datetime:"Date/heure",geo:"G\xE9o",country:"Pays",link:"Lien"},h=class extends b{constructor(){super(...arguments);this.baseTagsets=[];this.existingTags=[];this.tagsetProperties={};this.tagsetPropertyTypes={};this.graphEntities=[];this.heading="Ajouter \xE0 l'enqu\xEAte";this.createHeading="Cr\xE9er une entit\xE9";this.typePlaceholder="Type d'entit\xE9...";this.createLabel="Cr\xE9er";this.attachHeading="Ajouter comme propri\xE9t\xE9";this.chooseEntityLabel="Choisir une entit\xE9...";this.propertyPlaceholder="Type de l'information";this.attachLabel="Rattacher";this._selectedText="";this._selectedEntityId="";this._selectedPropertyType="";this._triggerVisible=!1;this._menuVisible=!1;this._triggerLeft=0;this._triggerTop=0;this._menuLeft=0;this._menuTop=0;this._onDocMouseUp=t=>{t.composedPath().includes(this)||window.setTimeout(()=>this._showTrigger(),0)};this._onDocClick=t=>{t.composedPath().includes(this)||this._close()};this._onDocKeyDown=t=>{t.key==="Escape"&&this._close()};this._onTriggerClick=()=>{let i=this.renderRoot.querySelector(".trigger")?.getBoundingClientRect(),s=i?i.left:this._triggerLeft,r=i?i.bottom+6:this._triggerTop,n=this._selectionText()||this._selectedText;if(!n){this._close();return}this._selectedText=n,this._selectedEntityId="",this._menuLeft=Math.min(Math.max(s,8),Math.max(8,window.innerWidth-316)),this._menuTop=Math.min(Math.max(r,8),Math.max(8,window.innerHeight-320)),this._triggerVisible=!1,this._menuVisible=!0};this._onEntityChange=t=>{this._selectedEntityId=t.target.value;let i=this.renderRoot.querySelector(".prop-input");this._selectedPropertyType=this._suggestedPropertyType(i?.value??"")};this._onPropertyInput=t=>{this._selectedPropertyType=this._suggestedPropertyType(t.target.value)};this._onPropertyTypeChange=t=>{this._selectedPropertyType=t.target.value};this._onCreate=()=>{let i=(this.renderRoot.querySelector(".type-input")?.value??"").trim();if(!i)return;let s=this._selectedText;this._close(),s&&this.dispatchEvent(new CustomEvent("synthesix-entity-create",{bubbles:!0,composed:!0,detail:{label:s,category:i}}))};this._onTypeKeydown=t=>{t.key==="Enter"&&(t.preventDefault(),this._onCreate())};this._onAttach=()=>{let t=this.renderRoot.querySelector(".entity-select"),i=this.renderRoot.querySelector(".prop-input"),s=t?.value??"",r=(i?.value??"").trim(),n=this._selectedPropertyType,c=this._selectedText;this._close(),!(!c||!s||!r)&&this.dispatchEvent(new CustomEvent("synthesix-entity-attach",{bubbles:!0,composed:!0,detail:{label:c,entityId:s,propertyKey:r,propertyType:n}}))};this._onPropKeydown=t=>{t.key==="Enter"&&(t.preventDefault(),this._onAttach())};this._stop=t=>t.stopPropagation()}connectedCallback(){super.connectedCallback(),document.addEventListener("mouseup",this._onDocMouseUp),document.addEventListener("click",this._onDocClick),document.addEventListener("keydown",this._onDocKeyDown,!0)}disconnectedCallback(){document.removeEventListener("mouseup",this._onDocMouseUp),document.removeEventListener("click",this._onDocClick),document.removeEventListener("keydown",this._onDocKeyDown,!0),super.disconnectedCallback()}_dedup(t){let i=new Set,s=[];for(let r of t){let n=String(r??"").trim(),c=n.toLowerCase();!n||i.has(c)||(i.add(c),s.push(n))}return s}get _typeSuggestions(){return this._dedup([...this.baseTagsets,...this.existingTags])}get _entities(){return this.graphEntities.filter(t=>String(t.id??"").trim())}get _propertySuggestions(){let t=this._entities.find(s=>String(s.id??"").trim()===String(this._selectedEntityId).trim());if(!t)return[];let i=[];for(let s of t.tags??[])i.push(...this.tagsetProperties[String(s??"").trim()]??[]);return i.push(...t.propertyKeys??[]),this._dedup(i)}_suggestedPropertyType(t){let i=String(t??"").trim().toLowerCase();if(!i)return"";let s=this._entities.find(r=>String(r.id??"").trim()===String(this._selectedEntityId).trim());for(let r of s?.tags??[]){let n=this.tagsetPropertyTypes[String(r??"").trim()]??{};for(let[c,l]of Object.entries(n))if(c.trim().toLowerCase()===i)return Object.prototype.hasOwnProperty.call(Tt,l)?l:""}return""}_selectionText(){return String(window.getSelection()?.toString()??"").replace(/\s+/g," ").trim().slice(0,200)}_close(){this._menuVisible=!1,this._triggerVisible=!1,this._selectedEntityId="",this._selectedPropertyType="";let t=this.renderRoot.querySelector(".type-input"),i=this.renderRoot.querySelector(".prop-input"),s=this.renderRoot.querySelector("select");t&&(t.value=""),i&&(i.value=""),s&&(s.value="")}_showTrigger(){let t=this._selectionText(),i=window.getSelection();if(!t||!i||i.rangeCount===0){this._close();return}let s=i.getRangeAt(0).getBoundingClientRect();if(!s||!s.width&&!s.height){this._close();return}this._selectedText=t,this._triggerLeft=Math.min(Math.max(s.left,8),Math.max(8,window.innerWidth-150)),this._triggerTop=Math.max(8,s.top-38),this._menuVisible=!1,this._triggerVisible=!0}render(){let t=this._entities.length>0,i=`display:${this._triggerVisible?"block":"none"};left:${this._triggerLeft}px;top:${this._triggerTop}px;`,s=`left:${this._menuLeft}px;top:${this._menuTop}px;`;return g`
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
            ${this._typeSuggestions.map(r=>g`<option value=${r}></option>`)}
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
            ${this._entities.map(r=>g`<option value=${r.id}>${r.label||r.id}</option>`)}
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
            ${this._propertySuggestions.map(r=>g`<option value=${r}></option>`)}
          </datalist>
          <select
            class="property-type-select"
            aria-label="Property type"
            .value=${this._selectedPropertyType}
            ?disabled=${!t}
            @change=${this._onPropertyTypeChange}
          >
            <option value="">Type auto</option>
            ${Object.entries(Tt).map(([r,n])=>g`<option value=${r}>${n}</option>`)}
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
    `}};h.styles=x`
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
      border: 1px solid #2b2d34;
      border-left: 3px solid #2a46a6;
      border-radius: 10px;
      background: #17181d;
      box-shadow: 0 18px 42px rgba(14, 15, 18, 0.4);
      color: #edeae2;
      font: 600 13px var(--font-ui, system-ui, Arial, sans-serif);
      z-index: 2147483647;
    }
    .menu.is-visible {
      display: block;
    }
    .title {
      padding: 1px 2px 2px;
      color: #8aa0ee;
      font: 600 11px var(--font-mono, monospace);
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }
    .preview {
      overflow: hidden;
      margin: 0 0 8px;
      padding: 0 2px;
      color: #f7f5ef;
      font: 600 13px var(--font-ui, system-ui, Arial, sans-serif);
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .create-title,
    .attach-title {
      padding: 0 2px 5px;
      color: #999488;
      font: 600 11px var(--font-mono, monospace);
      letter-spacing: 0.08em;
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
      border: 1px solid #2b2d34;
      border-radius: 7px;
      background: #1f2027;
      color: #f7f5ef;
      font: 600 13px var(--font-ui, system-ui, Arial, sans-serif);
    }
    input::placeholder {
      color: #999488;
    }
    input:focus,
    select:focus {
      border-color: #8aa0ee;
      box-shadow: 0 0 0 2px rgba(138, 160, 238, 0.2);
    }
    .type-input {
      flex: 1;
      min-width: 0;
    }
    .attach {
      margin-top: 3px;
      padding-top: 9px;
      border-top: 1px solid #262830;
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
      font: 700 13px var(--font-ui, system-ui, Arial, sans-serif);
      color: #ffffff;
    }
    .create-btn {
      padding: 8px 10px;
      background: #2a46a6;
    }
    .attach-btn {
      display: block;
      width: 100%;
      padding: 9px 10px;
      border: 1px solid #35406e;
      background: #2a46a6;
      text-align: center;
    }
    .create-btn:hover,
    .attach-btn:hover {
      background: #23408f;
    }
    button[disabled] {
      opacity: 0.55;
      cursor: not-allowed;
    }
  `,a([p({attribute:!1})],h.prototype,"baseTagsets",2),a([p({attribute:!1})],h.prototype,"existingTags",2),a([p({attribute:!1})],h.prototype,"tagsetProperties",2),a([p({attribute:!1})],h.prototype,"tagsetPropertyTypes",2),a([p({attribute:!1})],h.prototype,"graphEntities",2),a([p()],h.prototype,"heading",2),a([p()],h.prototype,"createHeading",2),a([p({attribute:"type-placeholder"})],h.prototype,"typePlaceholder",2),a([p({attribute:"create-label"})],h.prototype,"createLabel",2),a([p({attribute:"attach-heading"})],h.prototype,"attachHeading",2),a([p({attribute:"choose-entity-label"})],h.prototype,"chooseEntityLabel",2),a([p({attribute:"property-placeholder"})],h.prototype,"propertyPlaceholder",2),a([p({attribute:"attach-label"})],h.prototype,"attachLabel",2),a([v()],h.prototype,"_selectedText",2),a([v()],h.prototype,"_selectedEntityId",2),a([v()],h.prototype,"_selectedPropertyType",2),a([v()],h.prototype,"_triggerVisible",2),a([v()],h.prototype,"_menuVisible",2),a([v()],h.prototype,"_triggerLeft",2),a([v()],h.prototype,"_triggerTop",2),a([v()],h.prototype,"_menuLeft",2),a([v()],h.prototype,"_menuTop",2),h=a([$("sx-overlay-entity-menu")],h);var _=class extends b{constructor(){super(...arguments);this.variant="primary";this.state="idle";this.label="";this.titleText="";this.ariaText="";this.icon="none";this.iconOnly=!1;this.disabled=!1}render(){return g`
      <button
        type="button"
      >
        ${this.renderIcon()}
        <span data-label></span>
      </button>
    `}updated(){let t=this.renderRoot.querySelector("button"),i=this.getAttribute("label")||this.label;if(!t)return;let s=t.querySelector("[data-label]");s&&(s.textContent=i),t.disabled=this.disabled||this.hasAttribute("disabled"),t.title=this.getAttribute("title-text")||this.titleText||i,t.setAttribute("aria-label",this.getAttribute("aria-text")||this.ariaText||i)}renderIcon(){return this.icon==="mark"?g`
        <svg viewBox="0 0 48 48" aria-hidden="true">
          <line x1="6" y1="12" x2="33" y2="24" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"></line>
          <line x1="6" y1="24" x2="33" y2="24" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"></line>
          <line x1="6" y1="36" x2="33" y2="24" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"></line>
          <line x1="16" y1="6" x2="33" y2="24" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"></line>
          <line x1="16" y1="42" x2="33" y2="24" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"></line>
          <circle cx="6" cy="12" r="2.5" fill="#8AA0EE"></circle>
          <circle cx="6" cy="24" r="2.5" fill="#8AA0EE"></circle>
          <circle cx="6" cy="36" r="2.5" fill="#8AA0EE"></circle>
          <circle cx="16" cy="6" r="2.5" fill="#8AA0EE"></circle>
          <circle cx="16" cy="42" r="2.5" fill="#8AA0EE"></circle>
          <circle cx="34" cy="24" r="5.5" fill="#8AA0EE"></circle>
        </svg>
      `:this.icon==="archive"?g`
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M5 3h11l3 3v15H5zM8 3v6h8V3M8 14h8M8 18h6"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linejoin="round"
          ></path>
        </svg>
      `:this.icon==="camera"?g`
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
      `:f}};_.styles=x`
    ${k(A)}

    :host {
      display: inline-flex;
      --sx-action-bg: var(--accent, #2a46a6);
      --sx-action-border: var(--accent-strong, #23408f);
      --sx-action-hover: var(--accent-strong, #23408f);
      --sx-action-hover-border: var(--accent-ink, #17225a);
      --sx-action-text: #ffffff;
    }

    :host([variant="archive"]) {
      --sx-action-bg: var(--ink-surface, #17181d);
      --sx-action-border: var(--ink-border, #2b2d34);
      --sx-action-hover: var(--ink-border, #2b2d34);
      --sx-action-hover-border: #41434d;
      --sx-action-text: var(--on-ink-strong, #f7f5ef);
    }

    :host([variant="capture"]) {
      --sx-action-bg: var(--surface, #fbf9f4);
      --sx-action-border: var(--line, #dad4c7);
      --sx-action-hover: var(--surface-sunken, #ece8de);
      --sx-action-hover-border: #c9c2b2;
      --sx-action-text: var(--text, #191a1e);
    }

    :host([state="saving"]),
    :host([state="archiving"]),
    :host([state="capturing"]) {
      --sx-action-bg: #56513f;
      --sx-action-border: #56513f;
      --sx-action-hover: #56513f;
      --sx-action-hover-border: #56513f;
    }

    :host([state="saved"]),
    :host([state="archived"]),
    :host([state="captured"]) {
      --sx-action-bg: var(--success, #28613c);
      --sx-action-border: #1e4b2e;
      --sx-action-hover: #1e4b2e;
      --sx-action-hover-border: #173c25;
    }

    :host([state="error"]) {
      --sx-action-bg: var(--danger, #b33a3a);
      --sx-action-border: #8f2e2e;
      --sx-action-hover: #8f2e2e;
      --sx-action-hover-border: #742525;
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
      color: var(--sx-action-text);
      box-shadow: var(--shadow-soft, 0 8px 22px rgba(15, 23, 42, 0.18));
      cursor: pointer;
      font: 700 14px/1 var(--font-ui, system-ui, Arial, sans-serif);
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
      box-shadow: 0 12px 30px rgba(23, 24, 30, 0.34);
      transform: translateY(-1px);
    }

    button:focus-visible {
      outline: 3px solid rgba(138, 160, 238, 0.55);
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
  `,a([p({reflect:!0})],_.prototype,"variant",2),a([p({reflect:!0})],_.prototype,"state",2),a([p()],_.prototype,"label",2),a([p({attribute:"title-text"})],_.prototype,"titleText",2),a([p({attribute:"aria-text"})],_.prototype,"ariaText",2),a([p({reflect:!0})],_.prototype,"icon",2),a([p({type:Boolean,attribute:"icon-only",reflect:!0})],_.prototype,"iconOnly",2),a([p({type:Boolean,reflect:!0})],_.prototype,"disabled",2),_=a([$("sx-overlay-action")],_);var St="synthesix:external-overlay-position",C=16,Pt=200,Lt=170,P=class extends b{constructor(){super(...arguments);this.collapsed=!1;this.horizontalEdge="right";this.verticalEdge="bottom";this.dragState=null;this.handleResize=()=>{let t=this.getBoundingClientRect();if(!this.hasInlinePosition()){this.updateEdges(t.left,t.top,t.width,t.height);return}this.applyPosition(t.left,t.top,!1)};this.startDrag=t=>{if(t.button!==0)return;t.preventDefault(),t.stopPropagation();let i=this.getBoundingClientRect();t.currentTarget?.setPointerCapture?.(t.pointerId),this.dragState={height:i.height,pointerId:t.pointerId,startLeft:i.left,startTop:i.top,startX:t.clientX,startY:t.clientY,width:i.width},this.style.left=`${i.left}px`,this.style.top=`${i.top}px`,this.style.right="auto",this.style.bottom="auto",this.toggleAttribute("dragging",!0),window.addEventListener("pointermove",this.handleDragMove),window.addEventListener("pointerup",this.handleDragEnd),window.addEventListener("pointercancel",this.handleDragEnd)};this.handleDragMove=t=>{if(!this.dragState||t.pointerId!==this.dragState.pointerId)return;let i=this.dragState.startLeft+t.clientX-this.dragState.startX,s=this.dragState.startTop+t.clientY-this.dragState.startY;this.applyPosition(i,s,!1)};this.handleDragEnd=t=>{this.dragState&&t.pointerId!==this.dragState.pointerId||(this.persistPosition(),this.stopDrag())}}connectedCallback(){super.connectedCallback(),window.addEventListener("resize",this.handleResize)}disconnectedCallback(){window.removeEventListener("resize",this.handleResize),this.stopDrag(),super.disconnectedCallback()}firstUpdated(){this.restorePosition()}setCollapsed(t){if(this.collapsed===t)return;let i=this.getBoundingClientRect(),s=i.right,r=i.bottom,n=this.horizontalEdge,c=this.verticalEdge;this.collapsed=t,this.dispatchEvent(new CustomEvent("synthesix-overlay-toggle",{detail:{collapsed:this.collapsed},bubbles:!0,composed:!0})),this.updateComplete.then(()=>{let l=this.getBoundingClientRect(),u=n==="right"?s-l.width:i.left,m=c==="bottom"?r-l.height:i.top;this.applyPosition(u,m,!0)})}hasInlinePosition(){return this.style.left!==""&&this.style.top!==""}restorePosition(){try{let t=window.localStorage.getItem(St);if(!t){let s=this.getBoundingClientRect();this.updateEdges(s.left,s.top,s.width,s.height);return}let i=JSON.parse(t);if(typeof i.left!="number"||typeof i.top!="number")return;this.applyPosition(i.left,i.top,!1)}catch{let i=this.getBoundingClientRect();this.updateEdges(i.left,i.top,i.width,i.height)}}stopDrag(){this.dragState=null,this.toggleAttribute("dragging",!1),window.removeEventListener("pointermove",this.handleDragMove),window.removeEventListener("pointerup",this.handleDragEnd),window.removeEventListener("pointercancel",this.handleDragEnd)}applyPosition(t,i,s){let r=this.getBoundingClientRect(),n=r.width||this.dragState?.width||42,c=r.height||this.dragState?.height||36,l=this.clampPosition(t,i,n,c);this.style.left=`${l.left}px`,this.style.top=`${l.top}px`,this.style.right="auto",this.style.bottom="auto",this.updateEdges(l.left,l.top,n,c),s&&this.persistPosition()}clampPosition(t,i,s,r){let n=window.innerWidth||document.documentElement.clientWidth||s,c=window.innerHeight||document.documentElement.clientHeight||r,l=Math.max(C,n-s-C),u=Math.max(C,c-r-C);return{left:Math.min(Math.max(C,t),l),top:Math.min(Math.max(C,i),u)}}updateEdges(t,i,s,r){let n=window.innerWidth||document.documentElement.clientWidth||s,c=window.innerHeight||document.documentElement.clientHeight||r,l=n-t,u=t+s,m=c-i,d=i+r,E=t+s/2<n/2?"left":"right",w=i+r/2<c/2?"top":"bottom",D=l>=Pt+C?"left":u>=Pt+C?"right":l>=u?"left":"right",Ht=m>=Lt+C?"top":d>=Lt+C?"bottom":m>=d?"top":"bottom";this.horizontalEdge=E,this.verticalEdge=w,this.setAttribute("edge",E),this.setAttribute("vertical-edge",w),this.setAttribute("menu-edge",D),this.setAttribute("menu-vertical-edge",Ht)}persistPosition(){let t=this.getBoundingClientRect();try{window.localStorage.setItem(St,JSON.stringify({left:Math.round(t.left),top:Math.round(t.top)}))}catch{}}action(t){return this.querySelector(t)}setActionState(t,i,s,r){t&&(t.dataset.state=i,t.state=i,t.setAttribute("state",i),t.label=s,t.setAttribute("label",s),t.title=s,t.titleText=s,t.setAttribute("title-text",s),t.ariaText=s,t.setAttribute("aria-text",s),t.disabled=i===r,t.toggleAttribute("disabled",i===r))}setSaveButtonState(t,i){let s=this.action("[data-synthesix-save-page]");s&&(s.dataset.state=t,s.state=t,s.setAttribute("state",t),s.label=i,s.setAttribute("label",i),s.disabled=t==="saving",s.toggleAttribute("disabled",t==="saving"),s.titleText=s.title||i,s.setAttribute("title-text",s.title||i),s.ariaText=s.title||"Save page to active Synthesix investigation",s.setAttribute("aria-text",s.ariaText))}setCaptureState(t,i="Capture screenshot"){this.setActionState(this.action("[data-synthesix-capture]"),t,i,"capturing")}setArchiveState(t,i="Save page with HTML archive"){this.setActionState(this.action("[data-synthesix-archive]"),t,i,"archiving")}render(){return g`
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
          ${this.horizontalEdge==="left"?g`&lsaquo;`:g`&rsaquo;`}
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
    `}};P.styles=x`
    ${k(A)}

    :host {
      all: initial;
      box-sizing: border-box;
      position: fixed;
      right: 18px;
      bottom: 18px;
      z-index: 2147483647;
      display: block;
      color: var(--on-ink, #edeae2);
      font: 13px/1.2 var(--font-ui, system-ui, Arial, sans-serif);
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
      color: rgba(237, 234, 226, 0.95);
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
      background: rgba(23, 24, 29, 0.68);
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
      border: 1px solid rgba(218, 212, 199, 0.42);
      border-radius: 999px;
      background: rgba(23, 24, 29, 0.96);
      color: #f7f5ef;
      box-shadow: 0 10px 26px rgba(23, 24, 30, 0.26);
      cursor: pointer;
      font: 800 12px/1 var(--font-ui, system-ui, Arial, sans-serif);
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
      border-color: var(--accent, #2a46a6);
      background: var(--accent-strong, #23408f);
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
      background: rgba(23, 24, 29, 0.96);
      border: 1px solid rgba(218, 212, 199, 0.34);
      box-shadow: 0 10px 26px rgba(23, 24, 30, 0.2);
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
  `,a([p({type:Boolean,reflect:!0})],P.prototype,"collapsed",2),a([v()],P.prototype,"horizontalEdge",2),a([v()],P.prototype,"verticalEdge",2),P=a([$("sx-overlay-root")],P);window.SynthesixOverlay={tokensCss:A,version:"0.1.0"};var ki=A,Ot=o=>{let t=o.composedPath()[0]?.tagName;return t!=="INPUT"&&t!=="TEXTAREA"&&t!=="SELECT"?!1:o.composedPath().some(i=>{let s=i?.tagName;return typeof s=="string"&&s.startsWith("SX-OVERLAY-")})};for(let o of["keydown","keypress","keyup"])window.addEventListener(o,e=>{Ot(e)&&(e.stopImmediatePropagation(),e.stopPropagation())},!0);})();
