"use strict";(()=>{var xt=Object.defineProperty;var At=Object.getOwnPropertyDescriptor;var u=(o,t,e,s)=>{for(var r=s>1?void 0:s?At(t,e):t,i=o.length-1,n;i>=0;i--)(n=o[i])&&(r=(s?n(t,e,r):n(r))||r);return s&&r&&xt(t,e,r),r};var x=`
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
`;var B=globalThis,q=B.ShadowRoot&&(B.ShadyCSS===void 0||B.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,J=Symbol(),nt=new WeakMap,T=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==J)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(q&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=nt.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&nt.set(e,t))}return t}toString(){return this.cssText}},C=o=>new T(typeof o=="string"?o:o+"",void 0,J),M=(o,...t)=>{let e=o.length===1?o[0]:t.reduce((s,r,i)=>s+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+o[i+1],o[0]);return new T(e,o,J)},at=(o,t)=>{if(q)o.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),r=B.litNonce;r!==void 0&&s.setAttribute("nonce",r),s.textContent=e.cssText,o.appendChild(s)}},Y=q?o=>o:o=>o instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return C(e)})(o):o;var{is:Et,defineProperty:St,getOwnPropertyDescriptor:wt,getOwnPropertyNames:Ct,getOwnPropertySymbols:Pt,getPrototypeOf:kt}=Object,z=globalThis,ht=z.trustedTypes,Ut=ht?ht.emptyScript:"",Tt=z.reactiveElementPolyfillSupport,N=(o,t)=>o,R={toAttribute(o,t){switch(t){case Boolean:o=o?Ut:null;break;case Object:case Array:o=o==null?o:JSON.stringify(o)}return o},fromAttribute(o,t){let e=o;switch(t){case Boolean:e=o!==null;break;case Number:e=o===null?null:Number(o);break;case Object:case Array:try{e=JSON.parse(o)}catch{e=null}}return e}},I=(o,t)=>!Et(o,t),ct={attribute:!0,type:String,converter:R,reflect:!1,useDefault:!1,hasChanged:I};Symbol.metadata??=Symbol("metadata"),z.litPropertyMetadata??=new WeakMap;var $=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=ct){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),r=this.getPropertyDescriptor(t,s,e);r!==void 0&&St(this.prototype,t,r)}}static getPropertyDescriptor(t,e,s){let{get:r,set:i}=wt(this.prototype,t)??{get(){return this[e]},set(n){this[e]=n}};return{get:r,set(n){let h=r?.call(this);i?.call(this,n),this.requestUpdate(t,h,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??ct}static _$Ei(){if(this.hasOwnProperty(N("elementProperties")))return;let t=kt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(N("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(N("properties"))){let e=this.properties,s=[...Ct(e),...Pt(e)];for(let r of s)this.createProperty(r,e[r])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,r]of e)this.elementProperties.set(s,r)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let r=this._$Eu(e,s);r!==void 0&&this._$Eh.set(r,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let r of s)e.unshift(Y(r))}else t!==void 0&&e.push(Y(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return at(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),r=this.constructor._$Eu(t,s);if(r!==void 0&&s.reflect===!0){let i=(s.converter?.toAttribute!==void 0?s.converter:R).toAttribute(e,s.type);this._$Em=t,i==null?this.removeAttribute(r):this.setAttribute(r,i),this._$Em=null}}_$AK(t,e){let s=this.constructor,r=s._$Eh.get(t);if(r!==void 0&&this._$Em!==r){let i=s.getPropertyOptions(r),n=typeof i.converter=="function"?{fromAttribute:i.converter}:i.converter?.fromAttribute!==void 0?i.converter:R;this._$Em=r;let h=n.fromAttribute(e,i.type);this[r]=h??this._$Ej?.get(r)??h,this._$Em=null}}requestUpdate(t,e,s,r=!1,i){if(t!==void 0){let n=this.constructor;if(r===!1&&(i=this[t]),s??=n.getPropertyOptions(t),!((s.hasChanged??I)(i,e)||s.useDefault&&s.reflect&&i===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:r,wrapped:i},n){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),i!==!0||n!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),r===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[r,i]of this._$Ep)this[r]=i;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[r,i]of s){let{wrapped:n}=i,h=this[r];n!==!0||this._$AL.has(r)||h===void 0||this.C(r,void 0,i,h)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};$.elementStyles=[],$.shadowRootOptions={mode:"open"},$[N("elementProperties")]=new Map,$[N("finalized")]=new Map,Tt?.({ReactiveElement:$}),(z.reactiveElementVersions??=[]).push("2.1.2");var st=globalThis,lt=o=>o,V=st.trustedTypes,dt=V?V.createPolicy("lit-html",{createHTML:o=>o}):void 0,bt="$lit$",_=`lit$${Math.random().toFixed(9).slice(2)}$`,$t="?"+_,Mt=`<${$t}>`,S=document,O=()=>S.createComment(""),D=o=>o===null||typeof o!="object"&&typeof o!="function",rt=Array.isArray,Nt=o=>rt(o)||typeof o?.[Symbol.iterator]=="function",Z=`[ 	
\f\r]`,H=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,pt=/-->/g,ut=/>/g,A=RegExp(`>|${Z}(?:([^\\s"'>=/]+)(${Z}*=${Z}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),ft=/'/g,mt=/"/g,vt=/^(?:script|style|textarea|title)$/i,ot=o=>(t,...e)=>({_$litType$:o,strings:t,values:e}),y=ot(1),Vt=ot(2),Wt=ot(3),w=Symbol.for("lit-noChange"),l=Symbol.for("lit-nothing"),gt=new WeakMap,E=S.createTreeWalker(S,129);function _t(o,t){if(!rt(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return dt!==void 0?dt.createHTML(t):t}var Rt=(o,t)=>{let e=o.length-1,s=[],r,i=t===2?"<svg>":t===3?"<math>":"",n=H;for(let h=0;h<e;h++){let a=o[h],d,p,c=-1,b=0;for(;b<a.length&&(n.lastIndex=b,p=n.exec(a),p!==null);)b=n.lastIndex,n===H?p[1]==="!--"?n=pt:p[1]!==void 0?n=ut:p[2]!==void 0?(vt.test(p[2])&&(r=RegExp("</"+p[2],"g")),n=A):p[3]!==void 0&&(n=A):n===A?p[0]===">"?(n=r??H,c=-1):p[1]===void 0?c=-2:(c=n.lastIndex-p[2].length,d=p[1],n=p[3]===void 0?A:p[3]==='"'?mt:ft):n===mt||n===ft?n=A:n===pt||n===ut?n=H:(n=A,r=void 0);let v=n===A&&o[h+1].startsWith("/>")?" ":"";i+=n===H?a+Mt:c>=0?(s.push(d),a.slice(0,c)+bt+a.slice(c)+_+v):a+_+(c===-2?h:v)}return[_t(o,i+(o[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},F=class o{constructor({strings:t,_$litType$:e},s){let r;this.parts=[];let i=0,n=0,h=t.length-1,a=this.parts,[d,p]=Rt(t,e);if(this.el=o.createElement(d,s),E.currentNode=this.el.content,e===2||e===3){let c=this.el.content.firstChild;c.replaceWith(...c.childNodes)}for(;(r=E.nextNode())!==null&&a.length<h;){if(r.nodeType===1){if(r.hasAttributes())for(let c of r.getAttributeNames())if(c.endsWith(bt)){let b=p[n++],v=r.getAttribute(c).split(_),j=/([.?@])?(.*)/.exec(b);a.push({type:1,index:i,name:j[2],strings:v,ctor:j[1]==="."?Q:j[1]==="?"?X:j[1]==="@"?tt:k}),r.removeAttribute(c)}else c.startsWith(_)&&(a.push({type:6,index:i}),r.removeAttribute(c));if(vt.test(r.tagName)){let c=r.textContent.split(_),b=c.length-1;if(b>0){r.textContent=V?V.emptyScript:"";for(let v=0;v<b;v++)r.append(c[v],O()),E.nextNode(),a.push({type:2,index:++i});r.append(c[b],O())}}}else if(r.nodeType===8)if(r.data===$t)a.push({type:2,index:i});else{let c=-1;for(;(c=r.data.indexOf(_,c+1))!==-1;)a.push({type:7,index:i}),c+=_.length-1}i++}}static createElement(t,e){let s=S.createElement("template");return s.innerHTML=t,s}};function P(o,t,e=o,s){if(t===w)return t;let r=s!==void 0?e._$Co?.[s]:e._$Cl,i=D(t)?void 0:t._$litDirective$;return r?.constructor!==i&&(r?._$AO?.(!1),i===void 0?r=void 0:(r=new i(o),r._$AT(o,e,s)),s!==void 0?(e._$Co??=[])[s]=r:e._$Cl=r),r!==void 0&&(t=P(o,r._$AS(o,t.values),r,s)),t}var G=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,r=(t?.creationScope??S).importNode(e,!0);E.currentNode=r;let i=E.nextNode(),n=0,h=0,a=s[0];for(;a!==void 0;){if(n===a.index){let d;a.type===2?d=new L(i,i.nextSibling,this,t):a.type===1?d=new a.ctor(i,a.name,a.strings,this,t):a.type===6&&(d=new et(i,this,t)),this._$AV.push(d),a=s[++h]}n!==a?.index&&(i=E.nextNode(),n++)}return E.currentNode=S,r}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},L=class o{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,r){this.type=2,this._$AH=l,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=P(this,t,e),D(t)?t===l||t==null||t===""?(this._$AH!==l&&this._$AR(),this._$AH=l):t!==this._$AH&&t!==w&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Nt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==l&&D(this._$AH)?this._$AA.nextSibling.data=t:this.T(S.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,r=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=F.createElement(_t(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===r)this._$AH.p(e);else{let i=new G(r,this),n=i.u(this.options);i.p(e),this.T(n),this._$AH=i}}_$AC(t){let e=gt.get(t.strings);return e===void 0&&gt.set(t.strings,e=new F(t)),e}k(t){rt(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,r=0;for(let i of t)r===e.length?e.push(s=new o(this.O(O()),this.O(O()),this,this.options)):s=e[r],s._$AI(i),r++;r<e.length&&(this._$AR(s&&s._$AB.nextSibling,r),e.length=r)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=lt(t).nextSibling;lt(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},k=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,r,i){this.type=1,this._$AH=l,this._$AN=void 0,this.element=t,this.name=e,this._$AM=r,this.options=i,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=l}_$AI(t,e=this,s,r){let i=this.strings,n=!1;if(i===void 0)t=P(this,t,e,0),n=!D(t)||t!==this._$AH&&t!==w,n&&(this._$AH=t);else{let h=t,a,d;for(t=i[0],a=0;a<i.length-1;a++)d=P(this,h[s+a],e,a),d===w&&(d=this._$AH[a]),n||=!D(d)||d!==this._$AH[a],d===l?t=l:t!==l&&(t+=(d??"")+i[a+1]),this._$AH[a]=d}n&&!r&&this.j(t)}j(t){t===l?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},Q=class extends k{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===l?void 0:t}},X=class extends k{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==l)}},tt=class extends k{constructor(t,e,s,r,i){super(t,e,s,r,i),this.type=5}_$AI(t,e=this){if((t=P(this,t,e,0)??l)===w)return;let s=this._$AH,r=t===l&&s!==l||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,i=t!==l&&(s===l||r);r&&this.element.removeEventListener(this.name,this,s),i&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},et=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){P(this,t)}};var Ht=st.litHtmlPolyfillSupport;Ht?.(F,L),(st.litHtmlVersions??=[]).push("3.3.3");var yt=(o,t,e)=>{let s=e?.renderBefore??t,r=s._$litPart$;if(r===void 0){let i=e?.renderBefore??null;s._$litPart$=r=new L(t.insertBefore(O(),i),i,void 0,e??{})}return r._$AI(o),r};var it=globalThis,g=class extends ${constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=yt(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return w}};g._$litElement$=!0,g.finalized=!0,it.litElementHydrateSupport?.({LitElement:g});var Ot=it.litElementPolyfillSupport;Ot?.({LitElement:g});(it.litElementVersions??=[]).push("4.2.2");var W=o=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(o,t)}):customElements.define(o,t)};var Dt={attribute:!0,type:String,converter:R,reflect:!1,hasChanged:I},Ft=(o=Dt,t,e)=>{let{kind:s,metadata:r}=e,i=globalThis.litPropertyMetadata.get(r);if(i===void 0&&globalThis.litPropertyMetadata.set(r,i=new Map),s==="setter"&&((o=Object.create(o)).wrapped=!0),i.set(e.name,o),s==="accessor"){let{name:n}=e;return{set(h){let a=t.get.call(this);t.set.call(this,h),this.requestUpdate(n,a,o,!0,h)},init(h){return h!==void 0&&this.C(n,void 0,o,h),h}}}if(s==="setter"){let{name:n}=e;return function(h){let a=this[n];t.call(this,h),this.requestUpdate(n,a,o,!0,h)}}throw Error("Unsupported decorator location: "+s)};function m(o){return(t,e)=>typeof e=="object"?Ft(o,t,e):((s,r,i)=>{let n=r.hasOwnProperty(i);return r.constructor.createProperty(i,s),n?Object.getOwnPropertyDescriptor(r,i):void 0})(o,t,e)}var U=class extends g{constructor(){super(...arguments);this.open=!1}get captureName(){return this.input()?.value.trim()||""}set captureName(e){let s=this.input();s&&(s.value=e)}ensureCaptureName(e){let s=this.input();s&&!s.value.trim()&&(s.value=e)}reset(){this.captureName="",this.open=!1}firstUpdated(){this.renderRoot.querySelectorAll("[data-scope]").forEach(e=>{e.addEventListener("click",()=>{this.choose(e.dataset.scope)})})}render(){return y`
      <input
        type="text"
        maxlength="120"
        placeholder="Capture name (optional)"
        aria-label="Capture name"
      >
      <button type="button" data-scope="viewport">Visible area</button>
      <button type="button" data-scope="region">Select area</button>
    `}input(){return this.renderRoot.querySelector("input")}choose(e){this.open=!1,this.dispatchEvent(new CustomEvent("synthesix-capture-choice",{bubbles:!0,composed:!0,detail:{scope:e,captureName:this.captureName}}))}};U.styles=M`
    ${C(x)}

    :host {
      box-sizing: border-box;
      display: none;
      position: absolute;
      right: 0;
      bottom: 50px;
      width: 180px;
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

    input {
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
  `,u([m({type:Boolean,reflect:!0})],U.prototype,"open",2),U=u([W("sx-overlay-capture-menu")],U);var f=class extends g{constructor(){super(...arguments);this.variant="primary";this.state="idle";this.label="";this.titleText="";this.ariaText="";this.icon="none";this.iconOnly=!1;this.disabled=!1}render(){return y`
      <button
        type="button"
      >
        ${this.renderIcon()}
        <span data-label></span>
      </button>
    `}updated(){let e=this.renderRoot.querySelector("button"),s=this.getAttribute("label")||this.label;if(!e)return;let r=e.querySelector("[data-label]");r&&(r.textContent=s),e.disabled=this.disabled||this.hasAttribute("disabled"),e.title=this.getAttribute("title-text")||this.titleText||s,e.setAttribute("aria-label",this.getAttribute("aria-text")||this.ariaText||s)}renderIcon(){return this.icon==="mark"?y`
        <svg viewBox="0 0 128 128" aria-hidden="true">
          ${Array.from({length:10},(e,s)=>y`
            <path
              d="M58 12 69 6l9 38-12 9-9-7z"
              transform="rotate(${s*36} 64 64)"
              fill=${s%2===0?"#FFFFFF":"#67E8F9"}
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
      `:l}};f.styles=M`
    ${C(x)}

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
  `,u([m({reflect:!0})],f.prototype,"variant",2),u([m({reflect:!0})],f.prototype,"state",2),u([m()],f.prototype,"label",2),u([m({attribute:"title-text"})],f.prototype,"titleText",2),u([m({attribute:"aria-text"})],f.prototype,"ariaText",2),u([m({reflect:!0})],f.prototype,"icon",2),u([m({type:Boolean,attribute:"icon-only",reflect:!0})],f.prototype,"iconOnly",2),u([m({type:Boolean,reflect:!0})],f.prototype,"disabled",2),f=u([W("sx-overlay-action")],f);window.SynthesixOverlay={tokensCss:x,version:"0.1.0"};var Ve=x;})();
