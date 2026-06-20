"use strict";(()=>{var Mt=Object.defineProperty;var Dt=Object.getOwnPropertyDescriptor;var l=(r,e,t,i)=>{for(var s=i>1?void 0:i?Dt(e,t):e,o=r.length-1,n;o>=0;o--)(n=r[o])&&(s=(i?n(e,t,s):n(s))||s);return i&&s&&Mt(e,t,s),s};var w=`
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
`;var W=globalThis,G=W.ShadowRoot&&(W.ShadyCSS===void 0||W.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,tt=Symbol(),ht=new WeakMap,q=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==tt)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(G&&e===void 0){let i=t!==void 0&&t.length===1;i&&(e=ht.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&ht.set(t,e))}return e}toString(){return this.cssText}},A=r=>new q(typeof r=="string"?r:r+"",void 0,tt),x=(r,...e)=>{let t=r.length===1?r[0]:e.reduce((i,s,o)=>i+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+r[o+1],r[0]);return new q(t,r,tt)},ut=(r,e)=>{if(G)r.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let i=document.createElement("style"),s=W.litNonce;s!==void 0&&i.setAttribute("nonce",s),i.textContent=t.cssText,r.appendChild(i)}},et=G?r=>r:r=>r instanceof CSSStyleSheet?(e=>{let t="";for(let i of e.cssRules)t+=i.cssText;return A(t)})(r):r;var{is:Ht,defineProperty:Rt,getOwnPropertyDescriptor:Nt,getOwnPropertyNames:Ut,getOwnPropertySymbols:zt,getPrototypeOf:It}=Object,O=globalThis,gt=O.trustedTypes,qt=gt?gt.emptyScript:"",Ft=O.reactiveElementPolyfillSupport,F=(r,e)=>r,j={toAttribute(r,e){switch(e){case Boolean:r=r?qt:null;break;case Object:case Array:r=r==null?r:JSON.stringify(r)}return r},fromAttribute(r,e){let t=r;switch(e){case Boolean:t=r!==null;break;case Number:t=r===null?null:Number(r);break;case Object:case Array:try{t=JSON.parse(r)}catch{t=null}}return t}},J=(r,e)=>!Ht(r,e),bt={attribute:!0,type:String,converter:j,reflect:!1,useDefault:!1,hasChanged:J};Symbol.metadata??=Symbol("metadata"),O.litPropertyMetadata??=new WeakMap;var T=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=bt){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let i=Symbol(),s=this.getPropertyDescriptor(e,i,t);s!==void 0&&Rt(this.prototype,e,s)}}static getPropertyDescriptor(e,t,i){let{get:s,set:o}=Nt(this.prototype,e)??{get(){return this[t]},set(n){this[t]=n}};return{get:s,set(n){let c=s?.call(this);o?.call(this,n),this.requestUpdate(e,c,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??bt}static _$Ei(){if(this.hasOwnProperty(F("elementProperties")))return;let e=It(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(F("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(F("properties"))){let t=this.properties,i=[...Ut(t),...zt(t)];for(let s of i)this.createProperty(s,t[s])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[i,s]of t)this.elementProperties.set(i,s)}this._$Eh=new Map;for(let[t,i]of this.elementProperties){let s=this._$Eu(t,i);s!==void 0&&this._$Eh.set(s,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let i=new Set(e.flat(1/0).reverse());for(let s of i)t.unshift(et(s))}else e!==void 0&&t.push(et(e));return t}static _$Eu(e,t){let i=t.attribute;return i===!1?void 0:typeof i=="string"?i:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let i of t.keys())this.hasOwnProperty(i)&&(e.set(i,this[i]),delete this[i]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return ut(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$ET(e,t){let i=this.constructor.elementProperties.get(e),s=this.constructor._$Eu(e,i);if(s!==void 0&&i.reflect===!0){let o=(i.converter?.toAttribute!==void 0?i.converter:j).toAttribute(t,i.type);this._$Em=e,o==null?this.removeAttribute(s):this.setAttribute(s,o),this._$Em=null}}_$AK(e,t){let i=this.constructor,s=i._$Eh.get(e);if(s!==void 0&&this._$Em!==s){let o=i.getPropertyOptions(s),n=typeof o.converter=="function"?{fromAttribute:o.converter}:o.converter?.fromAttribute!==void 0?o.converter:j;this._$Em=s;let c=n.fromAttribute(t,o.type);this[s]=c??this._$Ej?.get(s)??c,this._$Em=null}}requestUpdate(e,t,i,s=!1,o){if(e!==void 0){let n=this.constructor;if(s===!1&&(o=this[e]),i??=n.getPropertyOptions(e),!((i.hasChanged??J)(o,t)||i.useDefault&&i.reflect&&o===this._$Ej?.get(e)&&!this.hasAttribute(n._$Eu(e,i))))return;this.C(e,t,i)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:i,reflect:s,wrapped:o},n){i&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,n??t??this[e]),o!==!0||n!==void 0)||(this._$AL.has(e)||(this.hasUpdated||i||(t=void 0),this._$AL.set(e,t)),s===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[s,o]of this._$Ep)this[s]=o;this._$Ep=void 0}let i=this.constructor.elementProperties;if(i.size>0)for(let[s,o]of i){let{wrapped:n}=o,c=this[s];n!==!0||this._$AL.has(s)||c===void 0||this.C(s,void 0,o,c)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(i=>i.hostUpdate?.()),this.update(t)):this._$EM()}catch(i){throw e=!1,this._$EM(),i}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};T.elementStyles=[],T.shadowRootOptions={mode:"open"},T[F("elementProperties")]=new Map,T[F("finalized")]=new Map,Ft?.({ReactiveElement:T}),(O.reactiveElementVersions??=[]).push("2.1.2");var lt=globalThis,mt=r=>r,Z=lt.trustedTypes,ft=Z?Z.createPolicy("lit-html",{createHTML:r=>r}):void 0,Et="$lit$",k=`lit$${Math.random().toFixed(9).slice(2)}$`,wt="?"+k,jt=`<${wt}>`,D=document,B=()=>D.createComment(""),K=r=>r===null||typeof r!="object"&&typeof r!="function",ct=Array.isArray,Vt=r=>ct(r)||typeof r?.[Symbol.iterator]=="function",it=`[ 	
\f\r]`,V=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,xt=/-->/g,vt=/>/g,L=RegExp(`>|${it}(?:([^\\s"'>=/]+)(${it}*=${it}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),yt=/'/g,_t=/"/g,At=/^(?:script|style|textarea|title)$/i,pt=r=>(e,...t)=>({_$litType$:r,strings:e,values:t}),b=pt(1),ee=pt(2),ie=pt(3),H=Symbol.for("lit-noChange"),m=Symbol.for("lit-nothing"),$t=new WeakMap,M=D.createTreeWalker(D,129);function Ct(r,e){if(!ct(r)||!r.hasOwnProperty("raw"))throw Error("invalid template strings array");return ft!==void 0?ft.createHTML(e):e}var Bt=(r,e)=>{let t=r.length-1,i=[],s,o=e===2?"<svg>":e===3?"<math>":"",n=V;for(let c=0;c<t;c++){let a=r[c],h,g,d=-1,y=0;for(;y<a.length&&(n.lastIndex=y,g=n.exec(a),g!==null);)y=n.lastIndex,n===V?g[1]==="!--"?n=xt:g[1]!==void 0?n=vt:g[2]!==void 0?(At.test(g[2])&&(s=RegExp("</"+g[2],"g")),n=L):g[3]!==void 0&&(n=L):n===L?g[0]===">"?(n=s??V,d=-1):g[1]===void 0?d=-2:(d=n.lastIndex-g[2].length,h=g[1],n=g[3]===void 0?L:g[3]==='"'?_t:yt):n===_t||n===yt?n=L:n===xt||n===vt?n=V:(n=L,s=void 0);let E=n===L&&r[c+1].startsWith("/>")?" ":"";o+=n===V?a+jt:d>=0?(i.push(h),a.slice(0,d)+Et+a.slice(d)+k+E):a+k+(d===-2?c:E)}return[Ct(r,o+(r[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),i]},X=class r{constructor({strings:e,_$litType$:t},i){let s;this.parts=[];let o=0,n=0,c=e.length-1,a=this.parts,[h,g]=Bt(e,t);if(this.el=r.createElement(h,i),M.currentNode=this.el.content,t===2||t===3){let d=this.el.content.firstChild;d.replaceWith(...d.childNodes)}for(;(s=M.nextNode())!==null&&a.length<c;){if(s.nodeType===1){if(s.hasAttributes())for(let d of s.getAttributeNames())if(d.endsWith(Et)){let y=g[n++],E=s.getAttribute(d).split(k),R=/([.?@])?(.*)/.exec(y);a.push({type:1,index:o,name:R[2],strings:E,ctor:R[1]==="."?ot:R[1]==="?"?rt:R[1]==="@"?nt:U}),s.removeAttribute(d)}else d.startsWith(k)&&(a.push({type:6,index:o}),s.removeAttribute(d));if(At.test(s.tagName)){let d=s.textContent.split(k),y=d.length-1;if(y>0){s.textContent=Z?Z.emptyScript:"";for(let E=0;E<y;E++)s.append(d[E],B()),M.nextNode(),a.push({type:2,index:++o});s.append(d[y],B())}}}else if(s.nodeType===8)if(s.data===wt)a.push({type:2,index:o});else{let d=-1;for(;(d=s.data.indexOf(k,d+1))!==-1;)a.push({type:7,index:o}),d+=k.length-1}o++}}static createElement(e,t){let i=D.createElement("template");return i.innerHTML=e,i}};function N(r,e,t=r,i){if(e===H)return e;let s=i!==void 0?t._$Co?.[i]:t._$Cl,o=K(e)?void 0:e._$litDirective$;return s?.constructor!==o&&(s?._$AO?.(!1),o===void 0?s=void 0:(s=new o(r),s._$AT(r,t,i)),i!==void 0?(t._$Co??=[])[i]=s:t._$Cl=s),s!==void 0&&(e=N(r,s._$AS(r,e.values),s,i)),e}var st=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:i}=this._$AD,s=(e?.creationScope??D).importNode(t,!0);M.currentNode=s;let o=M.nextNode(),n=0,c=0,a=i[0];for(;a!==void 0;){if(n===a.index){let h;a.type===2?h=new Y(o,o.nextSibling,this,e):a.type===1?h=new a.ctor(o,a.name,a.strings,this,e):a.type===6&&(h=new at(o,this,e)),this._$AV.push(h),a=i[++c]}n!==a?.index&&(o=M.nextNode(),n++)}return M.currentNode=D,s}p(e){let t=0;for(let i of this._$AV)i!==void 0&&(i.strings!==void 0?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}},Y=class r{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,s){this.type=2,this._$AH=m,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=N(this,e,t),K(e)?e===m||e==null||e===""?(this._$AH!==m&&this._$AR(),this._$AH=m):e!==this._$AH&&e!==H&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Vt(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==m&&K(this._$AH)?this._$AA.nextSibling.data=e:this.T(D.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:i}=e,s=typeof i=="number"?this._$AC(e):(i.el===void 0&&(i.el=X.createElement(Ct(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(t);else{let o=new st(s,this),n=o.u(this.options);o.p(t),this.T(n),this._$AH=o}}_$AC(e){let t=$t.get(e.strings);return t===void 0&&$t.set(e.strings,t=new X(e)),t}k(e){ct(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,i,s=0;for(let o of e)s===t.length?t.push(i=new r(this.O(B()),this.O(B()),this,this.options)):i=t[s],i._$AI(o),s++;s<t.length&&(this._$AR(i&&i._$AB.nextSibling,s),t.length=s)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let i=mt(e).nextSibling;mt(e).remove(),e=i}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},U=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,s,o){this.type=1,this._$AH=m,this._$AN=void 0,this.element=e,this.name=t,this._$AM=s,this.options=o,i.length>2||i[0]!==""||i[1]!==""?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=m}_$AI(e,t=this,i,s){let o=this.strings,n=!1;if(o===void 0)e=N(this,e,t,0),n=!K(e)||e!==this._$AH&&e!==H,n&&(this._$AH=e);else{let c=e,a,h;for(e=o[0],a=0;a<o.length-1;a++)h=N(this,c[i+a],t,a),h===H&&(h=this._$AH[a]),n||=!K(h)||h!==this._$AH[a],h===m?e=m:e!==m&&(e+=(h??"")+o[a+1]),this._$AH[a]=h}n&&!s&&this.j(e)}j(e){e===m?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},ot=class extends U{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===m?void 0:e}},rt=class extends U{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==m)}},nt=class extends U{constructor(e,t,i,s,o){super(e,t,i,s,o),this.type=5}_$AI(e,t=this){if((e=N(this,e,t,0)??m)===H)return;let i=this._$AH,s=e===m&&i!==m||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,o=e!==m&&(i===m||s);s&&this.element.removeEventListener(this.name,this,i),o&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},at=class{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){N(this,e)}};var Kt=lt.litHtmlPolyfillSupport;Kt?.(X,Y),(lt.litHtmlVersions??=[]).push("3.3.3");var St=(r,e,t)=>{let i=t?.renderBefore??e,s=i._$litPart$;if(s===void 0){let o=t?.renderBefore??null;i._$litPart$=s=new Y(e.insertBefore(B(),o),o,void 0,t??{})}return s._$AI(r),s};var dt=globalThis,f=class extends T{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=St(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return H}};f._$litElement$=!0,f.finalized=!0,dt.litElementHydrateSupport?.({LitElement:f});var Xt=dt.litElementPolyfillSupport;Xt?.({LitElement:f});(dt.litElementVersions??=[]).push("4.2.2");var _=r=>(e,t)=>{t!==void 0?t.addInitializer(()=>{customElements.define(r,e)}):customElements.define(r,e)};var Yt={attribute:!0,type:String,converter:j,reflect:!1,hasChanged:J},Wt=(r=Yt,e,t)=>{let{kind:i,metadata:s}=t,o=globalThis.litPropertyMetadata.get(s);if(o===void 0&&globalThis.litPropertyMetadata.set(s,o=new Map),i==="setter"&&((r=Object.create(r)).wrapped=!0),o.set(t.name,r),i==="accessor"){let{name:n}=t;return{set(c){let a=e.get.call(this);e.set.call(this,c),this.requestUpdate(n,a,r,!0,c)},init(c){return c!==void 0&&this.C(n,void 0,r,c),c}}}if(i==="setter"){let{name:n}=t;return function(c){let a=this[n];e.call(this,c),this.requestUpdate(n,a,r,!0,c)}}throw Error("Unsupported decorator location: "+i)};function p(r){return(e,t)=>typeof t=="object"?Wt(r,e,t):((i,s,o)=>{let n=s.hasOwnProperty(o);return s.constructor.createProperty(o,i),n?Object.getOwnPropertyDescriptor(s,o):void 0})(r,e,t)}function $(r){return p({...r,state:!0,attribute:!1})}var C=class extends f{constructor(){super(...arguments);this.open=!1;this.placeholder="Capture name (optional)";this.nameLabel="Capture name";this.viewportLabel="Visible area";this.regionLabel="Select area"}get captureName(){return this.input()?.value.trim()||""}set captureName(t){let i=this.input();i&&(i.value=t)}ensureCaptureName(t){let i=this.input();i&&!i.value.trim()&&(i.value=t)}reset(){this.captureName="",this.open=!1}firstUpdated(){this.renderRoot.querySelectorAll("[data-scope]").forEach(t=>{t.addEventListener("click",()=>{this.choose(t.dataset.scope)})})}render(){return b`
      <input
        type="text"
        maxlength="120"
        placeholder=${this.placeholder}
        aria-label=${this.nameLabel}
      >
      <button type="button" data-scope="viewport">${this.viewportLabel}</button>
      <button type="button" data-scope="region">${this.regionLabel}</button>
    `}input(){return this.renderRoot.querySelector("input")}choose(t){this.open=!1,this.dispatchEvent(new CustomEvent("synthesix-capture-choice",{bubbles:!0,composed:!0,detail:{scope:t,captureName:this.captureName}}))}};C.styles=x`
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
  `,l([p({type:Boolean,reflect:!0})],C.prototype,"open",2),l([p()],C.prototype,"placeholder",2),l([p({attribute:"name-label"})],C.prototype,"nameLabel",2),l([p({attribute:"viewport-label"})],C.prototype,"viewportLabel",2),l([p({attribute:"region-label"})],C.prototype,"regionLabel",2),C=l([_("sx-overlay-capture-menu")],C);var z=class extends f{constructor(){super(...arguments);this.label=""}render(){return b`<button type="button"></button>`}updated(){let t=this.renderRoot.querySelector("button");if(!t)return;let i=this.getAttribute("label")||this.label;t.textContent=i,t.setAttribute("aria-label",i)}};z.styles=x`
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
  `,l([p()],z.prototype,"label",2),z=l([_("sx-overlay-selection-trigger")],z);var I=class extends f{constructor(){super(...arguments);this.hint="Drag to select evidence \xB7 Esc to cancel";this._selecting=!1;this._startX=0;this._startY=0;this._onKeyDown=t=>{t.key==="Escape"&&(t.preventDefault(),this._emitCancel())};this._onPointerDown=t=>{t.preventDefault(),this._selecting=!0,this._startX=t.clientX,this._startY=t.clientY;let i=this._boxEl;i&&i.classList.add("is-active");try{this.setPointerCapture(t.pointerId)}catch{}};this._onPointerMove=t=>{if(!this._selecting)return;let i=this._boxEl;if(!i)return;let s=Math.min(this._startX,t.clientX),o=Math.min(this._startY,t.clientY);i.style.left=`${s}px`,i.style.top=`${o}px`,i.style.width=`${Math.abs(t.clientX-this._startX)}px`,i.style.height=`${Math.abs(t.clientY-this._startY)}px`};this._onPointerUp=t=>{if(!this._selecting)return;this._selecting=!1;let i=Math.min(this._startX,t.clientX),s=Math.min(this._startY,t.clientY),o=Math.abs(t.clientX-this._startX),n=Math.abs(t.clientY-this._startY);if(o<8||n<8){this._emitCancel();return}this.dispatchEvent(new CustomEvent("synthesix-region-selected",{bubbles:!0,composed:!0,detail:{x:i+window.scrollX,y:s+window.scrollY,width:o,height:n}}))}}connectedCallback(){super.connectedCallback(),document.addEventListener("keydown",this._onKeyDown,!0),this.addEventListener("pointerdown",this._onPointerDown),this.addEventListener("pointermove",this._onPointerMove),this.addEventListener("pointerup",this._onPointerUp)}disconnectedCallback(){document.removeEventListener("keydown",this._onKeyDown,!0),super.disconnectedCallback()}get _boxEl(){return this.renderRoot.querySelector(".box")}_emitCancel(){this.dispatchEvent(new CustomEvent("synthesix-region-cancel",{bubbles:!0,composed:!0}))}render(){return b`
      <div class="hint">${this.hint}</div>
      <div class="box"></div>
    `}};I.styles=x`
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
  `,l([p()],I.prototype,"hint",2),I=l([_("sx-overlay-selection-box")],I);var u=class extends f{constructor(){super(...arguments);this.baseTagsets=[];this.existingTags=[];this.tagsetProperties={};this.graphEntities=[];this.heading="Ajouter \xE0 l'enqu\xEAte";this.createHeading="Cr\xE9er une entit\xE9";this.typePlaceholder="Type d'entit\xE9...";this.createLabel="Cr\xE9er";this.attachHeading="Ajouter comme propri\xE9t\xE9";this.chooseEntityLabel="Choisir une entit\xE9...";this.propertyPlaceholder="Type de l'information";this.attachLabel="Rattacher";this._selectedText="";this._selectedEntityId="";this._triggerVisible=!1;this._menuVisible=!1;this._triggerLeft=0;this._triggerTop=0;this._menuLeft=0;this._menuTop=0;this._onDocMouseUp=t=>{t.composedPath().includes(this)||window.setTimeout(()=>this._showTrigger(),0)};this._onDocClick=t=>{t.composedPath().includes(this)||this._close()};this._onDocKeyDown=t=>{t.key==="Escape"&&this._close()};this._onTriggerClick=()=>{let i=this.renderRoot.querySelector(".trigger")?.getBoundingClientRect(),s=i?i.left:this._triggerLeft,o=i?i.bottom+6:this._triggerTop,n=this._selectionText()||this._selectedText;if(!n){this._close();return}this._selectedText=n,this._selectedEntityId="",this._menuLeft=Math.min(Math.max(s,8),Math.max(8,window.innerWidth-316)),this._menuTop=Math.min(Math.max(o,8),Math.max(8,window.innerHeight-320)),this._triggerVisible=!1,this._menuVisible=!0};this._onEntityChange=t=>{this._selectedEntityId=t.target.value};this._onCreate=()=>{let i=(this.renderRoot.querySelector(".type-input")?.value??"").trim();if(!i)return;let s=this._selectedText;this._close(),s&&this.dispatchEvent(new CustomEvent("synthesix-entity-create",{bubbles:!0,composed:!0,detail:{label:s,category:i}}))};this._onTypeKeydown=t=>{t.key==="Enter"&&(t.preventDefault(),this._onCreate())};this._onAttach=()=>{let t=this.renderRoot.querySelector("select"),i=this.renderRoot.querySelector(".prop-input"),s=t?.value??"",o=(i?.value??"").trim(),n=this._selectedText;this._close(),!(!n||!s||!o)&&this.dispatchEvent(new CustomEvent("synthesix-entity-attach",{bubbles:!0,composed:!0,detail:{label:n,entityId:s,propertyKey:o}}))};this._onPropKeydown=t=>{t.key==="Enter"&&(t.preventDefault(),this._onAttach())};this._stop=t=>t.stopPropagation()}connectedCallback(){super.connectedCallback(),document.addEventListener("mouseup",this._onDocMouseUp),document.addEventListener("click",this._onDocClick),document.addEventListener("keydown",this._onDocKeyDown,!0)}disconnectedCallback(){document.removeEventListener("mouseup",this._onDocMouseUp),document.removeEventListener("click",this._onDocClick),document.removeEventListener("keydown",this._onDocKeyDown,!0),super.disconnectedCallback()}_dedup(t){let i=new Set,s=[];for(let o of t){let n=String(o??"").trim(),c=n.toLowerCase();!n||i.has(c)||(i.add(c),s.push(n))}return s}get _typeSuggestions(){return this._dedup([...this.baseTagsets,...this.existingTags])}get _entities(){return this.graphEntities.filter(t=>String(t.id??"").trim())}get _propertySuggestions(){let t=this._entities.find(s=>String(s.id??"").trim()===String(this._selectedEntityId).trim());if(!t)return[];let i=[];for(let s of t.tags??[])i.push(...this.tagsetProperties[String(s??"").trim()]??[]);return i.push(...t.propertyKeys??[]),this._dedup(i)}_selectionText(){return String(window.getSelection()?.toString()??"").replace(/\s+/g," ").trim().slice(0,200)}_close(){this._menuVisible=!1,this._triggerVisible=!1,this._selectedEntityId="";let t=this.renderRoot.querySelector(".type-input"),i=this.renderRoot.querySelector(".prop-input"),s=this.renderRoot.querySelector("select");t&&(t.value=""),i&&(i.value=""),s&&(s.value="")}_showTrigger(){let t=this._selectionText(),i=window.getSelection();if(!t||!i||i.rangeCount===0){this._close();return}let s=i.getRangeAt(0).getBoundingClientRect();if(!s||!s.width&&!s.height){this._close();return}this._selectedText=t,this._triggerLeft=Math.min(Math.max(s.left,8),Math.max(8,window.innerWidth-150)),this._triggerTop=Math.max(8,s.top-38),this._menuVisible=!1,this._triggerVisible=!0}render(){let t=this._entities.length>0,i=`display:${this._triggerVisible?"block":"none"};left:${this._triggerLeft}px;top:${this._triggerTop}px;`,s=`left:${this._menuLeft}px;top:${this._menuTop}px;`;return b`
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
            ${this._typeSuggestions.map(o=>b`<option value=${o}></option>`)}
          </datalist>
        </div>
        <div class="attach">
          <div class="attach-title">${this.attachHeading}</div>
          <select ?disabled=${!t} @change=${this._onEntityChange}>
            <option value="">${this.chooseEntityLabel}</option>
            ${this._entities.map(o=>b`<option value=${o.id}>${o.label||o.id}</option>`)}
          </select>
          <input
            class="prop-input"
            type="text"
            maxlength="100"
            placeholder=${this.propertyPlaceholder}
            list="__sx-entity-props"
            @keydown=${this._onPropKeydown}
          >
          <datalist id="__sx-entity-props">
            ${this._propertySuggestions.map(o=>b`<option value=${o}></option>`)}
          </datalist>
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
    `}};u.styles=x`
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
      width: 300px;
      max-height: 390px;
      padding: 6px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      background: #ffffff;
      box-shadow: 0 14px 34px rgba(15, 23, 42, 0.28);
      color: #0f172a;
      font: 600 13px Arial, sans-serif;
      z-index: 2147483647;
    }
    .menu.is-visible {
      display: block;
    }
    .title {
      padding: 4px 6px 2px;
      color: #475569;
      font: 700 12px Arial, sans-serif;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .preview {
      overflow: hidden;
      padding: 0 6px 5px;
      color: #0f172a;
      font: 700 13px Arial, sans-serif;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .create-title,
    .attach-title {
      padding: 2px 6px 4px;
      color: #475569;
      font: 700 12px Arial, sans-serif;
    }
    .row {
      display: flex;
      gap: 5px;
      padding: 5px 0 4px;
    }
    input {
      all: initial;
      box-sizing: border-box;
      display: block;
      width: 100%;
      padding: 6px 7px;
      border: 1px solid #cbd5e1;
      border-radius: 5px;
      color: #0f172a;
      font: 500 13px Arial, sans-serif;
    }
    .type-input {
      flex: 1;
      min-width: 0;
    }
    select {
      all: initial;
      box-sizing: border-box;
      display: block;
      width: 100%;
      margin-bottom: 5px;
      padding: 6px 7px;
      border: 1px solid #cbd5e1;
      border-radius: 5px;
      background: #ffffff;
      color: #0f172a;
      font: 500 13px Arial, sans-serif;
    }
    .attach {
      margin-top: 5px;
      padding-top: 6px;
      border-top: 1px solid #e2e8f0;
    }
    .attach .prop-input {
      margin-bottom: 5px;
    }
    button {
      all: initial;
      box-sizing: border-box;
      border-radius: 5px;
      cursor: pointer;
      font: 700 13px Arial, sans-serif;
      color: #ffffff;
    }
    .create-btn {
      padding: 6px 9px;
      background: #2563eb;
    }
    .attach-btn {
      display: block;
      width: 100%;
      padding: 7px 9px;
      background: #0f172a;
      text-align: center;
    }
    button[disabled] {
      opacity: 0.55;
      cursor: not-allowed;
    }
  `,l([p({attribute:!1})],u.prototype,"baseTagsets",2),l([p({attribute:!1})],u.prototype,"existingTags",2),l([p({attribute:!1})],u.prototype,"tagsetProperties",2),l([p({attribute:!1})],u.prototype,"graphEntities",2),l([p()],u.prototype,"heading",2),l([p()],u.prototype,"createHeading",2),l([p({attribute:"type-placeholder"})],u.prototype,"typePlaceholder",2),l([p({attribute:"create-label"})],u.prototype,"createLabel",2),l([p({attribute:"attach-heading"})],u.prototype,"attachHeading",2),l([p({attribute:"choose-entity-label"})],u.prototype,"chooseEntityLabel",2),l([p({attribute:"property-placeholder"})],u.prototype,"propertyPlaceholder",2),l([p({attribute:"attach-label"})],u.prototype,"attachLabel",2),l([$()],u.prototype,"_selectedText",2),l([$()],u.prototype,"_selectedEntityId",2),l([$()],u.prototype,"_triggerVisible",2),l([$()],u.prototype,"_menuVisible",2),l([$()],u.prototype,"_triggerLeft",2),l([$()],u.prototype,"_triggerTop",2),l([$()],u.prototype,"_menuLeft",2),l([$()],u.prototype,"_menuTop",2),u=l([_("sx-overlay-entity-menu")],u);var v=class extends f{constructor(){super(...arguments);this.variant="primary";this.state="idle";this.label="";this.titleText="";this.ariaText="";this.icon="none";this.iconOnly=!1;this.disabled=!1}render(){return b`
      <button
        type="button"
      >
        ${this.renderIcon()}
        <span data-label></span>
      </button>
    `}updated(){let t=this.renderRoot.querySelector("button"),i=this.getAttribute("label")||this.label;if(!t)return;let s=t.querySelector("[data-label]");s&&(s.textContent=i),t.disabled=this.disabled||this.hasAttribute("disabled"),t.title=this.getAttribute("title-text")||this.titleText||i,t.setAttribute("aria-label",this.getAttribute("aria-text")||this.ariaText||i)}renderIcon(){return this.icon==="mark"?b`
        <svg viewBox="0 0 128 128" aria-hidden="true">
          ${Array.from({length:10},(t,i)=>b`
            <path
              d="M58 12 69 6l9 38-12 9-9-7z"
              transform="rotate(${i*36} 64 64)"
              fill=${i%2===0?"#FFFFFF":"#67E8F9"}
            ></path>
          `)}
          <circle cx="64" cy="64" r="14" fill="#FFFFFF"></circle>
        </svg>
      `:this.icon==="archive"?b`
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M5 3h11l3 3v15H5zM8 3v6h8V3M8 14h8M8 18h6"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linejoin="round"
          ></path>
        </svg>
      `:this.icon==="camera"?b`
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
      `:m}};v.styles=x`
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
  `,l([p({reflect:!0})],v.prototype,"variant",2),l([p({reflect:!0})],v.prototype,"state",2),l([p()],v.prototype,"label",2),l([p({attribute:"title-text"})],v.prototype,"titleText",2),l([p({attribute:"aria-text"})],v.prototype,"ariaText",2),l([p({reflect:!0})],v.prototype,"icon",2),l([p({type:Boolean,attribute:"icon-only",reflect:!0})],v.prototype,"iconOnly",2),l([p({type:Boolean,reflect:!0})],v.prototype,"disabled",2),v=l([_("sx-overlay-action")],v);var Tt="synthesix:external-overlay-position",S=16,kt=200,Pt=170,P=class extends f{constructor(){super(...arguments);this.collapsed=!1;this.horizontalEdge="right";this.verticalEdge="bottom";this.dragState=null;this.handleResize=()=>{let t=this.getBoundingClientRect();if(!this.hasInlinePosition()){this.updateEdges(t.left,t.top,t.width,t.height);return}this.applyPosition(t.left,t.top,!1)};this.startDrag=t=>{if(t.button!==0)return;t.preventDefault(),t.stopPropagation();let i=this.getBoundingClientRect();t.currentTarget?.setPointerCapture?.(t.pointerId),this.dragState={height:i.height,pointerId:t.pointerId,startLeft:i.left,startTop:i.top,startX:t.clientX,startY:t.clientY,width:i.width},this.style.left=`${i.left}px`,this.style.top=`${i.top}px`,this.style.right="auto",this.style.bottom="auto",this.toggleAttribute("dragging",!0),window.addEventListener("pointermove",this.handleDragMove),window.addEventListener("pointerup",this.handleDragEnd),window.addEventListener("pointercancel",this.handleDragEnd)};this.handleDragMove=t=>{if(!this.dragState||t.pointerId!==this.dragState.pointerId)return;let i=this.dragState.startLeft+t.clientX-this.dragState.startX,s=this.dragState.startTop+t.clientY-this.dragState.startY;this.applyPosition(i,s,!1)};this.handleDragEnd=t=>{this.dragState&&t.pointerId!==this.dragState.pointerId||(this.persistPosition(),this.stopDrag())}}connectedCallback(){super.connectedCallback(),window.addEventListener("resize",this.handleResize)}disconnectedCallback(){window.removeEventListener("resize",this.handleResize),this.stopDrag(),super.disconnectedCallback()}firstUpdated(){this.restorePosition()}setCollapsed(t){if(this.collapsed===t)return;let i=this.getBoundingClientRect(),s=i.right,o=i.bottom,n=this.horizontalEdge,c=this.verticalEdge;this.collapsed=t,this.dispatchEvent(new CustomEvent("synthesix-overlay-toggle",{detail:{collapsed:this.collapsed},bubbles:!0,composed:!0})),this.updateComplete.then(()=>{let a=this.getBoundingClientRect(),h=n==="right"?s-a.width:i.left,g=c==="bottom"?o-a.height:i.top;this.applyPosition(h,g,!0)})}hasInlinePosition(){return this.style.left!==""&&this.style.top!==""}restorePosition(){try{let t=window.localStorage.getItem(Tt);if(!t){let s=this.getBoundingClientRect();this.updateEdges(s.left,s.top,s.width,s.height);return}let i=JSON.parse(t);if(typeof i.left!="number"||typeof i.top!="number")return;this.applyPosition(i.left,i.top,!1)}catch{let i=this.getBoundingClientRect();this.updateEdges(i.left,i.top,i.width,i.height)}}stopDrag(){this.dragState=null,this.toggleAttribute("dragging",!1),window.removeEventListener("pointermove",this.handleDragMove),window.removeEventListener("pointerup",this.handleDragEnd),window.removeEventListener("pointercancel",this.handleDragEnd)}applyPosition(t,i,s){let o=this.getBoundingClientRect(),n=o.width||this.dragState?.width||42,c=o.height||this.dragState?.height||36,a=this.clampPosition(t,i,n,c);this.style.left=`${a.left}px`,this.style.top=`${a.top}px`,this.style.right="auto",this.style.bottom="auto",this.updateEdges(a.left,a.top,n,c),s&&this.persistPosition()}clampPosition(t,i,s,o){let n=window.innerWidth||document.documentElement.clientWidth||s,c=window.innerHeight||document.documentElement.clientHeight||o,a=Math.max(S,n-s-S),h=Math.max(S,c-o-S);return{left:Math.min(Math.max(S,t),a),top:Math.min(Math.max(S,i),h)}}updateEdges(t,i,s,o){let n=window.innerWidth||document.documentElement.clientWidth||s,c=window.innerHeight||document.documentElement.clientHeight||o,a=n-t,h=t+s,g=c-i,d=i+o,y=t+s/2<n/2?"left":"right",E=i+o/2<c/2?"top":"bottom",R=a>=kt+S?"left":h>=kt+S?"right":a>=h?"left":"right",Lt=g>=Pt+S?"top":d>=Pt+S?"bottom":g>=d?"top":"bottom";this.horizontalEdge=y,this.verticalEdge=E,this.setAttribute("edge",y),this.setAttribute("vertical-edge",E),this.setAttribute("menu-edge",R),this.setAttribute("menu-vertical-edge",Lt)}persistPosition(){let t=this.getBoundingClientRect();try{window.localStorage.setItem(Tt,JSON.stringify({left:Math.round(t.left),top:Math.round(t.top)}))}catch{}}action(t){return this.querySelector(t)}setActionState(t,i,s,o){t&&(t.dataset.state=i,t.state=i,t.setAttribute("state",i),t.label=s,t.setAttribute("label",s),t.title=s,t.titleText=s,t.setAttribute("title-text",s),t.ariaText=s,t.setAttribute("aria-text",s),t.disabled=i===o,t.toggleAttribute("disabled",i===o))}setSaveButtonState(t,i){let s=this.action("[data-synthesix-save-page]");s&&(s.dataset.state=t,s.state=t,s.setAttribute("state",t),s.label=i,s.setAttribute("label",i),s.disabled=t==="saving",s.toggleAttribute("disabled",t==="saving"),s.titleText=s.title||i,s.setAttribute("title-text",s.title||i),s.ariaText=s.title||"Save page to active Synthesix investigation",s.setAttribute("aria-text",s.ariaText))}setCaptureState(t,i="Capture screenshot"){this.setActionState(this.action("[data-synthesix-capture]"),t,i,"capturing")}setArchiveState(t,i="Save page with HTML archive"){this.setActionState(this.action("[data-synthesix-archive]"),t,i,"archiving")}render(){return b`
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
          ${this.horizontalEdge==="left"?b`&lsaquo;`:b`&rsaquo;`}
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
  `,l([p({type:Boolean,reflect:!0})],P.prototype,"collapsed",2),l([$()],P.prototype,"horizontalEdge",2),l([$()],P.prototype,"verticalEdge",2),P=l([_("sx-overlay-root")],P);window.SynthesixOverlay={tokensCss:w,version:"0.1.0"};var wi=w;})();
