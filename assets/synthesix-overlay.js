"use strict";(()=>{var Ht=Object.defineProperty;var Rt=Object.getOwnPropertyDescriptor;var l=(r,e,t,s)=>{for(var i=s>1?void 0:s?Rt(e,t):e,o=r.length-1,n;o>=0;o--)(n=r[o])&&(i=(s?n(e,t,i):n(i))||i);return s&&i&&Ht(e,t,i),i};var w=`
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
`;var W=globalThis,O=W.ShadowRoot&&(W.ShadyCSS===void 0||W.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,tt=Symbol(),ht=new WeakMap,q=class{constructor(e,t,s){if(this._$cssResult$=!0,s!==tt)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(O&&e===void 0){let s=t!==void 0&&t.length===1;s&&(e=ht.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),s&&ht.set(t,e))}return e}toString(){return this.cssText}},A=r=>new q(typeof r=="string"?r:r+"",void 0,tt),v=(r,...e)=>{let t=r.length===1?r[0]:e.reduce((s,i,o)=>s+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+r[o+1],r[0]);return new q(t,r,tt)},ut=(r,e)=>{if(O)r.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let s=document.createElement("style"),i=W.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=t.cssText,r.appendChild(s)}},et=O?r=>r:r=>r instanceof CSSStyleSheet?(e=>{let t="";for(let s of e.cssRules)t+=s.cssText;return A(t)})(r):r;var{is:Dt,defineProperty:Nt,getOwnPropertyDescriptor:Ut,getOwnPropertyNames:It,getOwnPropertySymbols:zt,getPrototypeOf:qt}=Object,G=globalThis,gt=G.trustedTypes,jt=gt?gt.emptyScript:"",Ft=G.reactiveElementPolyfillSupport,j=(r,e)=>r,F={toAttribute(r,e){switch(e){case Boolean:r=r?jt:null;break;case Object:case Array:r=r==null?r:JSON.stringify(r)}return r},fromAttribute(r,e){let t=r;switch(e){case Boolean:t=r!==null;break;case Number:t=r===null?null:Number(r);break;case Object:case Array:try{t=JSON.parse(r)}catch{t=null}}return t}},J=(r,e)=>!Dt(r,e),mt={attribute:!0,type:String,converter:F,reflect:!1,useDefault:!1,hasChanged:J};Symbol.metadata??=Symbol("metadata"),G.litPropertyMetadata??=new WeakMap;var S=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=mt){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(e,s,t);i!==void 0&&Nt(this.prototype,e,i)}}static getPropertyDescriptor(e,t,s){let{get:i,set:o}=Ut(this.prototype,e)??{get(){return this[t]},set(n){this[t]=n}};return{get:i,set(n){let c=i?.call(this);o?.call(this,n),this.requestUpdate(e,c,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??mt}static _$Ei(){if(this.hasOwnProperty(j("elementProperties")))return;let e=qt(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(j("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(j("properties"))){let t=this.properties,s=[...It(t),...zt(t)];for(let i of s)this.createProperty(i,t[i])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[s,i]of t)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[t,s]of this.elementProperties){let i=this._$Eu(t,s);i!==void 0&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let s=new Set(e.flat(1/0).reverse());for(let i of s)t.unshift(et(i))}else e!==void 0&&t.push(et(e));return t}static _$Eu(e,t){let s=t.attribute;return s===!1?void 0:typeof s=="string"?s:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let s of t.keys())this.hasOwnProperty(s)&&(e.set(s,this[s]),delete this[s]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return ut(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,s){this._$AK(e,s)}_$ET(e,t){let s=this.constructor.elementProperties.get(e),i=this.constructor._$Eu(e,s);if(i!==void 0&&s.reflect===!0){let o=(s.converter?.toAttribute!==void 0?s.converter:F).toAttribute(t,s.type);this._$Em=e,o==null?this.removeAttribute(i):this.setAttribute(i,o),this._$Em=null}}_$AK(e,t){let s=this.constructor,i=s._$Eh.get(e);if(i!==void 0&&this._$Em!==i){let o=s.getPropertyOptions(i),n=typeof o.converter=="function"?{fromAttribute:o.converter}:o.converter?.fromAttribute!==void 0?o.converter:F;this._$Em=i;let c=n.fromAttribute(t,o.type);this[i]=c??this._$Ej?.get(i)??c,this._$Em=null}}requestUpdate(e,t,s,i=!1,o){if(e!==void 0){let n=this.constructor;if(i===!1&&(o=this[e]),s??=n.getPropertyOptions(e),!((s.hasChanged??J)(o,t)||s.useDefault&&s.reflect&&o===this._$Ej?.get(e)&&!this.hasAttribute(n._$Eu(e,s))))return;this.C(e,t,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:s,reflect:i,wrapped:o},n){s&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,n??t??this[e]),o!==!0||n!==void 0)||(this._$AL.has(e)||(this.hasUpdated||s||(t=void 0),this._$AL.set(e,t)),i===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,o]of this._$Ep)this[i]=o;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,o]of s){let{wrapped:n}=o,c=this[i];n!==!0||this._$AL.has(i)||c===void 0||this.C(i,void 0,o,c)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(t)):this._$EM()}catch(s){throw e=!1,this._$EM(),s}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};S.elementStyles=[],S.shadowRootOptions={mode:"open"},S[j("elementProperties")]=new Map,S[j("finalized")]=new Map,Ft?.({ReactiveElement:S}),(G.reactiveElementVersions??=[]).push("2.1.2");var lt=globalThis,bt=r=>r,Z=lt.trustedTypes,ft=Z?Z.createPolicy("lit-html",{createHTML:r=>r}):void 0,Et="$lit$",P=`lit$${Math.random().toFixed(9).slice(2)}$`,wt="?"+P,Vt=`<${wt}>`,H=document,B=()=>H.createComment(""),K=r=>r===null||typeof r!="object"&&typeof r!="function",ct=Array.isArray,Bt=r=>ct(r)||typeof r?.[Symbol.iterator]=="function",st=`[ 	
\f\r]`,V=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,vt=/-->/g,xt=/>/g,L=RegExp(`>|${st}(?:([^\\s"'>=/]+)(${st}*=${st}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),yt=/'/g,_t=/"/g,At=/^(?:script|style|textarea|title)$/i,pt=r=>(e,...t)=>({_$litType$:r,strings:e,values:t}),g=pt(1),se=pt(2),ie=pt(3),R=Symbol.for("lit-noChange"),b=Symbol.for("lit-nothing"),$t=new WeakMap,M=H.createTreeWalker(H,129);function Ct(r,e){if(!ct(r)||!r.hasOwnProperty("raw"))throw Error("invalid template strings array");return ft!==void 0?ft.createHTML(e):e}var Kt=(r,e)=>{let t=r.length-1,s=[],i,o=e===2?"<svg>":e===3?"<math>":"",n=V;for(let c=0;c<t;c++){let a=r[c],u,m,d=-1,_=0;for(;_<a.length&&(n.lastIndex=_,m=n.exec(a),m!==null);)_=n.lastIndex,n===V?m[1]==="!--"?n=vt:m[1]!==void 0?n=xt:m[2]!==void 0?(At.test(m[2])&&(i=RegExp("</"+m[2],"g")),n=L):m[3]!==void 0&&(n=L):n===L?m[0]===">"?(n=i??V,d=-1):m[1]===void 0?d=-2:(d=n.lastIndex-m[2].length,u=m[1],n=m[3]===void 0?L:m[3]==='"'?_t:yt):n===_t||n===yt?n=L:n===vt||n===xt?n=V:(n=L,i=void 0);let E=n===L&&r[c+1].startsWith("/>")?" ":"";o+=n===V?a+Vt:d>=0?(s.push(u),a.slice(0,d)+Et+a.slice(d)+P+E):a+P+(d===-2?c:E)}return[Ct(r,o+(r[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),s]},X=class r{constructor({strings:e,_$litType$:t},s){let i;this.parts=[];let o=0,n=0,c=e.length-1,a=this.parts,[u,m]=Kt(e,t);if(this.el=r.createElement(u,s),M.currentNode=this.el.content,t===2||t===3){let d=this.el.content.firstChild;d.replaceWith(...d.childNodes)}for(;(i=M.nextNode())!==null&&a.length<c;){if(i.nodeType===1){if(i.hasAttributes())for(let d of i.getAttributeNames())if(d.endsWith(Et)){let _=m[n++],E=i.getAttribute(d).split(P),D=/([.?@])?(.*)/.exec(_);a.push({type:1,index:o,name:D[2],strings:E,ctor:D[1]==="."?ot:D[1]==="?"?rt:D[1]==="@"?nt:U}),i.removeAttribute(d)}else d.startsWith(P)&&(a.push({type:6,index:o}),i.removeAttribute(d));if(At.test(i.tagName)){let d=i.textContent.split(P),_=d.length-1;if(_>0){i.textContent=Z?Z.emptyScript:"";for(let E=0;E<_;E++)i.append(d[E],B()),M.nextNode(),a.push({type:2,index:++o});i.append(d[_],B())}}}else if(i.nodeType===8)if(i.data===wt)a.push({type:2,index:o});else{let d=-1;for(;(d=i.data.indexOf(P,d+1))!==-1;)a.push({type:7,index:o}),d+=P.length-1}o++}}static createElement(e,t){let s=H.createElement("template");return s.innerHTML=e,s}};function N(r,e,t=r,s){if(e===R)return e;let i=s!==void 0?t._$Co?.[s]:t._$Cl,o=K(e)?void 0:e._$litDirective$;return i?.constructor!==o&&(i?._$AO?.(!1),o===void 0?i=void 0:(i=new o(r),i._$AT(r,t,s)),s!==void 0?(t._$Co??=[])[s]=i:t._$Cl=i),i!==void 0&&(e=N(r,i._$AS(r,e.values),i,s)),e}var it=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:s}=this._$AD,i=(e?.creationScope??H).importNode(t,!0);M.currentNode=i;let o=M.nextNode(),n=0,c=0,a=s[0];for(;a!==void 0;){if(n===a.index){let u;a.type===2?u=new Y(o,o.nextSibling,this,e):a.type===1?u=new a.ctor(o,a.name,a.strings,this,e):a.type===6&&(u=new at(o,this,e)),this._$AV.push(u),a=s[++c]}n!==a?.index&&(o=M.nextNode(),n++)}return M.currentNode=H,i}p(e){let t=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(e,s,t),t+=s.strings.length-2):s._$AI(e[t])),t++}},Y=class r{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,s,i){this.type=2,this._$AH=b,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=N(this,e,t),K(e)?e===b||e==null||e===""?(this._$AH!==b&&this._$AR(),this._$AH=b):e!==this._$AH&&e!==R&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Bt(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==b&&K(this._$AH)?this._$AA.nextSibling.data=e:this.T(H.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:s}=e,i=typeof s=="number"?this._$AC(e):(s.el===void 0&&(s.el=X.createElement(Ct(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(t);else{let o=new it(i,this),n=o.u(this.options);o.p(t),this.T(n),this._$AH=o}}_$AC(e){let t=$t.get(e.strings);return t===void 0&&$t.set(e.strings,t=new X(e)),t}k(e){ct(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,s,i=0;for(let o of e)i===t.length?t.push(s=new r(this.O(B()),this.O(B()),this,this.options)):s=t[i],s._$AI(o),i++;i<t.length&&(this._$AR(s&&s._$AB.nextSibling,i),t.length=i)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let s=bt(e).nextSibling;bt(e).remove(),e=s}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},U=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,s,i,o){this.type=1,this._$AH=b,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=o,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=b}_$AI(e,t=this,s,i){let o=this.strings,n=!1;if(o===void 0)e=N(this,e,t,0),n=!K(e)||e!==this._$AH&&e!==R,n&&(this._$AH=e);else{let c=e,a,u;for(e=o[0],a=0;a<o.length-1;a++)u=N(this,c[s+a],t,a),u===R&&(u=this._$AH[a]),n||=!K(u)||u!==this._$AH[a],u===b?e=b:e!==b&&(e+=(u??"")+o[a+1]),this._$AH[a]=u}n&&!i&&this.j(e)}j(e){e===b?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},ot=class extends U{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===b?void 0:e}},rt=class extends U{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==b)}},nt=class extends U{constructor(e,t,s,i,o){super(e,t,s,i,o),this.type=5}_$AI(e,t=this){if((e=N(this,e,t,0)??b)===R)return;let s=this._$AH,i=e===b&&s!==b||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,o=e!==b&&(s===b||i);i&&this.element.removeEventListener(this.name,this,s),o&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},at=class{constructor(e,t,s){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(e){N(this,e)}};var Xt=lt.litHtmlPolyfillSupport;Xt?.(X,Y),(lt.litHtmlVersions??=[]).push("3.3.3");var Tt=(r,e,t)=>{let s=t?.renderBefore??e,i=s._$litPart$;if(i===void 0){let o=t?.renderBefore??null;s._$litPart$=i=new Y(e.insertBefore(B(),o),o,void 0,t??{})}return i._$AI(r),i};var dt=globalThis,f=class extends S{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Tt(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return R}};f._$litElement$=!0,f.finalized=!0,dt.litElementHydrateSupport?.({LitElement:f});var Yt=dt.litElementPolyfillSupport;Yt?.({LitElement:f});(dt.litElementVersions??=[]).push("4.2.2");var $=r=>(e,t)=>{t!==void 0?t.addInitializer(()=>{customElements.define(r,e)}):customElements.define(r,e)};var Wt={attribute:!0,type:String,converter:F,reflect:!1,hasChanged:J},Ot=(r=Wt,e,t)=>{let{kind:s,metadata:i}=t,o=globalThis.litPropertyMetadata.get(i);if(o===void 0&&globalThis.litPropertyMetadata.set(i,o=new Map),s==="setter"&&((r=Object.create(r)).wrapped=!0),o.set(t.name,r),s==="accessor"){let{name:n}=t;return{set(c){let a=e.get.call(this);e.set.call(this,c),this.requestUpdate(n,a,r,!0,c)},init(c){return c!==void 0&&this.C(n,void 0,r,c),c}}}if(s==="setter"){let{name:n}=t;return function(c){let a=this[n];e.call(this,c),this.requestUpdate(n,a,r,!0,c)}}throw Error("Unsupported decorator location: "+s)};function p(r){return(e,t)=>typeof t=="object"?Ot(r,e,t):((s,i,o)=>{let n=i.hasOwnProperty(o);return i.constructor.createProperty(o,s),n?Object.getOwnPropertyDescriptor(i,o):void 0})(r,e,t)}function x(r){return p({...r,state:!0,attribute:!1})}var C=class extends f{constructor(){super(...arguments);this.open=!1;this.placeholder="Capture name (optional)";this.nameLabel="Capture name";this.viewportLabel="Visible area";this.regionLabel="Select area"}get captureName(){return this.input()?.value.trim()||""}set captureName(t){let s=this.input();s&&(s.value=t)}ensureCaptureName(t){let s=this.input();s&&!s.value.trim()&&(s.value=t)}reset(){this.captureName="",this.open=!1}firstUpdated(){this.renderRoot.querySelectorAll("[data-scope]").forEach(t=>{t.addEventListener("click",()=>{this.choose(t.dataset.scope)})})}render(){return g`
      <input
        type="text"
        maxlength="120"
        placeholder=${this.placeholder}
        aria-label=${this.nameLabel}
      >
      <button type="button" data-scope="viewport">${this.viewportLabel}</button>
      <button type="button" data-scope="region">${this.regionLabel}</button>
    `}input(){return this.renderRoot.querySelector("input")}choose(t){this.open=!1,this.dispatchEvent(new CustomEvent("synthesix-capture-choice",{bubbles:!0,composed:!0,detail:{scope:t,captureName:this.captureName}}))}};C.styles=v`
    ${A(w)}

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
  `,l([p({type:Boolean,reflect:!0})],C.prototype,"open",2),l([p()],C.prototype,"placeholder",2),l([p({attribute:"name-label"})],C.prototype,"nameLabel",2),l([p({attribute:"viewport-label"})],C.prototype,"viewportLabel",2),l([p({attribute:"region-label"})],C.prototype,"regionLabel",2),C=l([$("sx-overlay-capture-menu")],C);var I=class extends f{constructor(){super(...arguments);this.label=""}render(){return g`<button type="button"></button>`}updated(){let t=this.renderRoot.querySelector("button");if(!t)return;let s=this.getAttribute("label")||this.label;t.textContent=s,t.setAttribute("aria-label",s)}};I.styles=v`
    ${A(w)}

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
  `,l([p()],I.prototype,"label",2),I=l([$("sx-overlay-selection-trigger")],I);var z=class extends f{constructor(){super(...arguments);this.hint="Drag to select evidence \xB7 Esc to cancel";this._selecting=!1;this._startX=0;this._startY=0;this._onKeyDown=t=>{t.key==="Escape"&&(t.preventDefault(),this._emitCancel())};this._onPointerDown=t=>{t.preventDefault(),this._selecting=!0,this._startX=t.clientX,this._startY=t.clientY;let s=this._boxEl;s&&s.classList.add("is-active");try{this.setPointerCapture(t.pointerId)}catch{}};this._onPointerMove=t=>{if(!this._selecting)return;let s=this._boxEl;if(!s)return;let i=Math.min(this._startX,t.clientX),o=Math.min(this._startY,t.clientY);s.style.left=`${i}px`,s.style.top=`${o}px`,s.style.width=`${Math.abs(t.clientX-this._startX)}px`,s.style.height=`${Math.abs(t.clientY-this._startY)}px`};this._onPointerUp=t=>{if(!this._selecting)return;this._selecting=!1;let s=Math.min(this._startX,t.clientX),i=Math.min(this._startY,t.clientY),o=Math.abs(t.clientX-this._startX),n=Math.abs(t.clientY-this._startY);if(o<8||n<8){this._emitCancel();return}this.dispatchEvent(new CustomEvent("synthesix-region-selected",{bubbles:!0,composed:!0,detail:{x:s+window.scrollX,y:i+window.scrollY,width:o,height:n}}))}}connectedCallback(){super.connectedCallback(),document.addEventListener("keydown",this._onKeyDown,!0),this.addEventListener("pointerdown",this._onPointerDown),this.addEventListener("pointermove",this._onPointerMove),this.addEventListener("pointerup",this._onPointerUp)}disconnectedCallback(){document.removeEventListener("keydown",this._onKeyDown,!0),super.disconnectedCallback()}get _boxEl(){return this.renderRoot.querySelector(".box")}_emitCancel(){this.dispatchEvent(new CustomEvent("synthesix-region-cancel",{bubbles:!0,composed:!0}))}render(){return g`
      <div class="hint">${this.hint}</div>
      <div class="box"></div>
    `}};z.styles=v`
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
  `,l([p()],z.prototype,"hint",2),z=l([$("sx-overlay-selection-box")],z);var St={text:"Texte",number:"Nombre",date:"Date",datetime:"Date/heure",geo:"G\xE9o",country:"Pays",link:"Lien"},h=class extends f{constructor(){super(...arguments);this.baseTagsets=[];this.existingTags=[];this.tagsetProperties={};this.tagsetPropertyTypes={};this.graphEntities=[];this.heading="Ajouter \xE0 l'enqu\xEAte";this.createHeading="Cr\xE9er une entit\xE9";this.typePlaceholder="Type d'entit\xE9...";this.createLabel="Cr\xE9er";this.attachHeading="Ajouter comme propri\xE9t\xE9";this.chooseEntityLabel="Choisir une entit\xE9...";this.propertyPlaceholder="Type de l'information";this.attachLabel="Rattacher";this._selectedText="";this._selectedEntityId="";this._selectedPropertyType="";this._triggerVisible=!1;this._menuVisible=!1;this._triggerLeft=0;this._triggerTop=0;this._menuLeft=0;this._menuTop=0;this._onDocMouseUp=t=>{t.composedPath().includes(this)||window.setTimeout(()=>this._showTrigger(),0)};this._onDocClick=t=>{t.composedPath().includes(this)||this._close()};this._onDocKeyDown=t=>{t.key==="Escape"&&this._close()};this._onTriggerClick=()=>{let s=this.renderRoot.querySelector(".trigger")?.getBoundingClientRect(),i=s?s.left:this._triggerLeft,o=s?s.bottom+6:this._triggerTop,n=this._selectionText()||this._selectedText;if(!n){this._close();return}this._selectedText=n,this._selectedEntityId="",this._menuLeft=Math.min(Math.max(i,8),Math.max(8,window.innerWidth-316)),this._menuTop=Math.min(Math.max(o,8),Math.max(8,window.innerHeight-320)),this._triggerVisible=!1,this._menuVisible=!0};this._onEntityChange=t=>{this._selectedEntityId=t.target.value;let s=this.renderRoot.querySelector(".prop-input");this._selectedPropertyType=this._suggestedPropertyType(s?.value??"")};this._onPropertyInput=t=>{this._selectedPropertyType=this._suggestedPropertyType(t.target.value)};this._onPropertyTypeChange=t=>{this._selectedPropertyType=t.target.value};this._onCreate=()=>{let s=(this.renderRoot.querySelector(".type-input")?.value??"").trim();if(!s)return;let i=this._selectedText;this._close(),i&&this.dispatchEvent(new CustomEvent("synthesix-entity-create",{bubbles:!0,composed:!0,detail:{label:i,category:s}}))};this._onTypeKeydown=t=>{t.key==="Enter"&&(t.preventDefault(),this._onCreate())};this._onAttach=()=>{let t=this.renderRoot.querySelector(".entity-select"),s=this.renderRoot.querySelector(".prop-input"),i=t?.value??"",o=(s?.value??"").trim(),n=this._selectedPropertyType,c=this._selectedText;this._close(),!(!c||!i||!o)&&this.dispatchEvent(new CustomEvent("synthesix-entity-attach",{bubbles:!0,composed:!0,detail:{label:c,entityId:i,propertyKey:o,propertyType:n}}))};this._onPropKeydown=t=>{t.key==="Enter"&&(t.preventDefault(),this._onAttach())};this._stop=t=>t.stopPropagation()}connectedCallback(){super.connectedCallback(),document.addEventListener("mouseup",this._onDocMouseUp),document.addEventListener("click",this._onDocClick),document.addEventListener("keydown",this._onDocKeyDown,!0)}disconnectedCallback(){document.removeEventListener("mouseup",this._onDocMouseUp),document.removeEventListener("click",this._onDocClick),document.removeEventListener("keydown",this._onDocKeyDown,!0),super.disconnectedCallback()}_dedup(t){let s=new Set,i=[];for(let o of t){let n=String(o??"").trim(),c=n.toLowerCase();!n||s.has(c)||(s.add(c),i.push(n))}return i}get _typeSuggestions(){return this._dedup([...this.baseTagsets,...this.existingTags])}get _entities(){return this.graphEntities.filter(t=>String(t.id??"").trim())}get _propertySuggestions(){let t=this._entities.find(i=>String(i.id??"").trim()===String(this._selectedEntityId).trim());if(!t)return[];let s=[];for(let i of t.tags??[])s.push(...this.tagsetProperties[String(i??"").trim()]??[]);return s.push(...t.propertyKeys??[]),this._dedup(s)}_suggestedPropertyType(t){let s=String(t??"").trim().toLowerCase();if(!s)return"";let i=this._entities.find(o=>String(o.id??"").trim()===String(this._selectedEntityId).trim());for(let o of i?.tags??[]){let n=this.tagsetPropertyTypes[String(o??"").trim()]??{};for(let[c,a]of Object.entries(n))if(c.trim().toLowerCase()===s)return Object.prototype.hasOwnProperty.call(St,a)?a:""}return""}_selectionText(){return String(window.getSelection()?.toString()??"").replace(/\s+/g," ").trim().slice(0,200)}_close(){this._menuVisible=!1,this._triggerVisible=!1,this._selectedEntityId="",this._selectedPropertyType="";let t=this.renderRoot.querySelector(".type-input"),s=this.renderRoot.querySelector(".prop-input"),i=this.renderRoot.querySelector("select");t&&(t.value=""),s&&(s.value=""),i&&(i.value="")}_showTrigger(){let t=this._selectionText(),s=window.getSelection();if(!t||!s||s.rangeCount===0){this._close();return}let i=s.getRangeAt(0).getBoundingClientRect();if(!i||!i.width&&!i.height){this._close();return}this._selectedText=t,this._triggerLeft=Math.min(Math.max(i.left,8),Math.max(8,window.innerWidth-150)),this._triggerTop=Math.max(8,i.top-38),this._menuVisible=!1,this._triggerVisible=!0}render(){let t=this._entities.length>0,s=`display:${this._triggerVisible?"block":"none"};left:${this._triggerLeft}px;top:${this._triggerTop}px;`,i=`left:${this._menuLeft}px;top:${this._menuTop}px;`;return g`
      <sx-overlay-selection-trigger
        class="trigger"
        style=${s}
        label=${this.heading}
        @click=${this._onTriggerClick}
      ></sx-overlay-selection-trigger>
      <div
        class="menu ${this._menuVisible?"is-visible":""}"
        style=${i}
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
            ${this._typeSuggestions.map(o=>g`<option value=${o}></option>`)}
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
            ${this._entities.map(o=>g`<option value=${o.id}>${o.label||o.id}</option>`)}
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
            ${this._propertySuggestions.map(o=>g`<option value=${o}></option>`)}
          </datalist>
          <select
            class="property-type-select"
            aria-label="Property type"
            .value=${this._selectedPropertyType}
            ?disabled=${!t}
            @change=${this._onPropertyTypeChange}
          >
            <option value="">Type auto</option>
            ${Object.entries(St).map(([o,n])=>g`<option value=${o}>${n}</option>`)}
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
    `}};h.styles=v`
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
  `,l([p({attribute:!1})],h.prototype,"baseTagsets",2),l([p({attribute:!1})],h.prototype,"existingTags",2),l([p({attribute:!1})],h.prototype,"tagsetProperties",2),l([p({attribute:!1})],h.prototype,"tagsetPropertyTypes",2),l([p({attribute:!1})],h.prototype,"graphEntities",2),l([p()],h.prototype,"heading",2),l([p()],h.prototype,"createHeading",2),l([p({attribute:"type-placeholder"})],h.prototype,"typePlaceholder",2),l([p({attribute:"create-label"})],h.prototype,"createLabel",2),l([p({attribute:"attach-heading"})],h.prototype,"attachHeading",2),l([p({attribute:"choose-entity-label"})],h.prototype,"chooseEntityLabel",2),l([p({attribute:"property-placeholder"})],h.prototype,"propertyPlaceholder",2),l([p({attribute:"attach-label"})],h.prototype,"attachLabel",2),l([x()],h.prototype,"_selectedText",2),l([x()],h.prototype,"_selectedEntityId",2),l([x()],h.prototype,"_selectedPropertyType",2),l([x()],h.prototype,"_triggerVisible",2),l([x()],h.prototype,"_menuVisible",2),l([x()],h.prototype,"_triggerLeft",2),l([x()],h.prototype,"_triggerTop",2),l([x()],h.prototype,"_menuLeft",2),l([x()],h.prototype,"_menuTop",2),h=l([$("sx-overlay-entity-menu")],h);var y=class extends f{constructor(){super(...arguments);this.variant="primary";this.state="idle";this.label="";this.titleText="";this.ariaText="";this.icon="none";this.iconOnly=!1;this.disabled=!1}render(){return g`
      <button
        type="button"
      >
        ${this.renderIcon()}
        <span data-label></span>
      </button>
    `}updated(){let t=this.renderRoot.querySelector("button"),s=this.getAttribute("label")||this.label;if(!t)return;let i=t.querySelector("[data-label]");i&&(i.textContent=s),t.disabled=this.disabled||this.hasAttribute("disabled"),t.title=this.getAttribute("title-text")||this.titleText||s,t.setAttribute("aria-label",this.getAttribute("aria-text")||this.ariaText||s)}renderIcon(){return this.icon==="mark"?g`
        <svg viewBox="0 0 128 128" aria-hidden="true">
          ${Array.from({length:10},(t,s)=>g`
            <path
              d="M58 12 69 6l9 38-12 9-9-7z"
              transform="rotate(${s*36} 64 64)"
              fill=${s%2===0?"#FFFFFF":"#67E8F9"}
            ></path>
          `)}
          <circle cx="64" cy="64" r="14" fill="#FFFFFF"></circle>
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
      `:b}};y.styles=v`
    ${A(w)}

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
  `,l([p({reflect:!0})],y.prototype,"variant",2),l([p({reflect:!0})],y.prototype,"state",2),l([p()],y.prototype,"label",2),l([p({attribute:"title-text"})],y.prototype,"titleText",2),l([p({attribute:"aria-text"})],y.prototype,"ariaText",2),l([p({reflect:!0})],y.prototype,"icon",2),l([p({type:Boolean,attribute:"icon-only",reflect:!0})],y.prototype,"iconOnly",2),l([p({type:Boolean,reflect:!0})],y.prototype,"disabled",2),y=l([$("sx-overlay-action")],y);var Pt="synthesix:external-overlay-position",T=16,kt=200,Lt=170,k=class extends f{constructor(){super(...arguments);this.collapsed=!1;this.horizontalEdge="right";this.verticalEdge="bottom";this.dragState=null;this.handleResize=()=>{let t=this.getBoundingClientRect();if(!this.hasInlinePosition()){this.updateEdges(t.left,t.top,t.width,t.height);return}this.applyPosition(t.left,t.top,!1)};this.startDrag=t=>{if(t.button!==0)return;t.preventDefault(),t.stopPropagation();let s=this.getBoundingClientRect();t.currentTarget?.setPointerCapture?.(t.pointerId),this.dragState={height:s.height,pointerId:t.pointerId,startLeft:s.left,startTop:s.top,startX:t.clientX,startY:t.clientY,width:s.width},this.style.left=`${s.left}px`,this.style.top=`${s.top}px`,this.style.right="auto",this.style.bottom="auto",this.toggleAttribute("dragging",!0),window.addEventListener("pointermove",this.handleDragMove),window.addEventListener("pointerup",this.handleDragEnd),window.addEventListener("pointercancel",this.handleDragEnd)};this.handleDragMove=t=>{if(!this.dragState||t.pointerId!==this.dragState.pointerId)return;let s=this.dragState.startLeft+t.clientX-this.dragState.startX,i=this.dragState.startTop+t.clientY-this.dragState.startY;this.applyPosition(s,i,!1)};this.handleDragEnd=t=>{this.dragState&&t.pointerId!==this.dragState.pointerId||(this.persistPosition(),this.stopDrag())}}connectedCallback(){super.connectedCallback(),window.addEventListener("resize",this.handleResize)}disconnectedCallback(){window.removeEventListener("resize",this.handleResize),this.stopDrag(),super.disconnectedCallback()}firstUpdated(){this.restorePosition()}setCollapsed(t){if(this.collapsed===t)return;let s=this.getBoundingClientRect(),i=s.right,o=s.bottom,n=this.horizontalEdge,c=this.verticalEdge;this.collapsed=t,this.dispatchEvent(new CustomEvent("synthesix-overlay-toggle",{detail:{collapsed:this.collapsed},bubbles:!0,composed:!0})),this.updateComplete.then(()=>{let a=this.getBoundingClientRect(),u=n==="right"?i-a.width:s.left,m=c==="bottom"?o-a.height:s.top;this.applyPosition(u,m,!0)})}hasInlinePosition(){return this.style.left!==""&&this.style.top!==""}restorePosition(){try{let t=window.localStorage.getItem(Pt);if(!t){let i=this.getBoundingClientRect();this.updateEdges(i.left,i.top,i.width,i.height);return}let s=JSON.parse(t);if(typeof s.left!="number"||typeof s.top!="number")return;this.applyPosition(s.left,s.top,!1)}catch{let s=this.getBoundingClientRect();this.updateEdges(s.left,s.top,s.width,s.height)}}stopDrag(){this.dragState=null,this.toggleAttribute("dragging",!1),window.removeEventListener("pointermove",this.handleDragMove),window.removeEventListener("pointerup",this.handleDragEnd),window.removeEventListener("pointercancel",this.handleDragEnd)}applyPosition(t,s,i){let o=this.getBoundingClientRect(),n=o.width||this.dragState?.width||42,c=o.height||this.dragState?.height||36,a=this.clampPosition(t,s,n,c);this.style.left=`${a.left}px`,this.style.top=`${a.top}px`,this.style.right="auto",this.style.bottom="auto",this.updateEdges(a.left,a.top,n,c),i&&this.persistPosition()}clampPosition(t,s,i,o){let n=window.innerWidth||document.documentElement.clientWidth||i,c=window.innerHeight||document.documentElement.clientHeight||o,a=Math.max(T,n-i-T),u=Math.max(T,c-o-T);return{left:Math.min(Math.max(T,t),a),top:Math.min(Math.max(T,s),u)}}updateEdges(t,s,i,o){let n=window.innerWidth||document.documentElement.clientWidth||i,c=window.innerHeight||document.documentElement.clientHeight||o,a=n-t,u=t+i,m=c-s,d=s+o,_=t+i/2<n/2?"left":"right",E=s+o/2<c/2?"top":"bottom",D=a>=kt+T?"left":u>=kt+T?"right":a>=u?"left":"right",Mt=m>=Lt+T?"top":d>=Lt+T?"bottom":m>=d?"top":"bottom";this.horizontalEdge=_,this.verticalEdge=E,this.setAttribute("edge",_),this.setAttribute("vertical-edge",E),this.setAttribute("menu-edge",D),this.setAttribute("menu-vertical-edge",Mt)}persistPosition(){let t=this.getBoundingClientRect();try{window.localStorage.setItem(Pt,JSON.stringify({left:Math.round(t.left),top:Math.round(t.top)}))}catch{}}action(t){return this.querySelector(t)}setActionState(t,s,i,o){t&&(t.dataset.state=s,t.state=s,t.setAttribute("state",s),t.label=i,t.setAttribute("label",i),t.title=i,t.titleText=i,t.setAttribute("title-text",i),t.ariaText=i,t.setAttribute("aria-text",i),t.disabled=s===o,t.toggleAttribute("disabled",s===o))}setSaveButtonState(t,s){let i=this.action("[data-synthesix-save-page]");i&&(i.dataset.state=t,i.state=t,i.setAttribute("state",t),i.label=s,i.setAttribute("label",s),i.disabled=t==="saving",i.toggleAttribute("disabled",t==="saving"),i.titleText=i.title||s,i.setAttribute("title-text",i.title||s),i.ariaText=i.title||"Save page to active Synthesix investigation",i.setAttribute("aria-text",i.ariaText))}setCaptureState(t,s="Capture screenshot"){this.setActionState(this.action("[data-synthesix-capture]"),t,s,"capturing")}setArchiveState(t,s="Save page with HTML archive"){this.setActionState(this.action("[data-synthesix-archive]"),t,s,"archiving")}render(){return g`
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
    `}};k.styles=v`
    ${A(w)}

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
  `,l([p({type:Boolean,reflect:!0})],k.prototype,"collapsed",2),l([x()],k.prototype,"horizontalEdge",2),l([x()],k.prototype,"verticalEdge",2),k=l([$("sx-overlay-root")],k);window.SynthesixOverlay={tokensCss:w,version:"0.1.0"};var As=w;})();
