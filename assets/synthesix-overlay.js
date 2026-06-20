"use strict";(()=>{var St=Object.defineProperty;var kt=Object.getOwnPropertyDescriptor;var a=(r,t,e,s)=>{for(var i=s>1?void 0:s?kt(t,e):t,o=r.length-1,n;o>=0;o--)(n=r[o])&&(i=(s?n(t,e,i):n(i))||i);return s&&i&&St(t,e,i),i};var y=`
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
`;var B=globalThis,W=B.ShadowRoot&&(B.ShadyCSS===void 0||B.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Q=Symbol(),ht=new WeakMap,q=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==Q)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(W&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=ht.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&ht.set(e,t))}return t}toString(){return this.cssText}},$=r=>new q(typeof r=="string"?r:r+"",void 0,Q),x=(r,...t)=>{let e=r.length===1?r[0]:t.reduce((s,i,o)=>s+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+r[o+1],r[0]);return new q(e,r,Q)},dt=(r,t)=>{if(W)r.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),i=B.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=e.cssText,r.appendChild(s)}},tt=W?r=>r:r=>r instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return $(e)})(r):r;var{is:Tt,defineProperty:Pt,getOwnPropertyDescriptor:Lt,getOwnPropertyNames:Mt,getOwnPropertySymbols:Ht,getPrototypeOf:Rt}=Object,G=globalThis,ut=G.trustedTypes,Ut=ut?ut.emptyScript:"",Dt=G.reactiveElementPolyfillSupport,z=(r,t)=>r,j={toAttribute(r,t){switch(t){case Boolean:r=r?Ut:null;break;case Object:case Array:r=r==null?r:JSON.stringify(r)}return r},fromAttribute(r,t){let e=r;switch(t){case Boolean:e=r!==null;break;case Number:e=r===null?null:Number(r);break;case Object:case Array:try{e=JSON.parse(r)}catch{e=null}}return e}},J=(r,t)=>!Tt(r,t),ft={attribute:!0,type:String,converter:j,reflect:!1,useDefault:!1,hasChanged:J};Symbol.metadata??=Symbol("metadata"),G.litPropertyMetadata??=new WeakMap;var w=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=ft){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(t,s,e);i!==void 0&&Pt(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){let{get:i,set:o}=Lt(this.prototype,t)??{get(){return this[e]},set(n){this[e]=n}};return{get:i,set(n){let p=i?.call(this);o?.call(this,n),this.requestUpdate(t,p,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??ft}static _$Ei(){if(this.hasOwnProperty(z("elementProperties")))return;let t=Rt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(z("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(z("properties"))){let e=this.properties,s=[...Mt(e),...Ht(e)];for(let i of s)this.createProperty(i,e[i])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,i]of e)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let i=this._$Eu(e,s);i!==void 0&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let i of s)e.unshift(tt(i))}else t!==void 0&&e.push(tt(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return dt(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),i=this.constructor._$Eu(t,s);if(i!==void 0&&s.reflect===!0){let o=(s.converter?.toAttribute!==void 0?s.converter:j).toAttribute(e,s.type);this._$Em=t,o==null?this.removeAttribute(i):this.setAttribute(i,o),this._$Em=null}}_$AK(t,e){let s=this.constructor,i=s._$Eh.get(t);if(i!==void 0&&this._$Em!==i){let o=s.getPropertyOptions(i),n=typeof o.converter=="function"?{fromAttribute:o.converter}:o.converter?.fromAttribute!==void 0?o.converter:j;this._$Em=i;let p=n.fromAttribute(e,o.type);this[i]=p??this._$Ej?.get(i)??p,this._$Em=null}}requestUpdate(t,e,s,i=!1,o){if(t!==void 0){let n=this.constructor;if(i===!1&&(o=this[t]),s??=n.getPropertyOptions(t),!((s.hasChanged??J)(o,e)||s.useDefault&&s.reflect&&o===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:i,wrapped:o},n){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),o!==!0||n!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),i===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,o]of this._$Ep)this[i]=o;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,o]of s){let{wrapped:n}=o,p=this[i];n!==!0||this._$AL.has(i)||p===void 0||this.C(i,void 0,o,p)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};w.elementStyles=[],w.shadowRootOptions={mode:"open"},w[z("elementProperties")]=new Map,w[z("finalized")]=new Map,Dt?.({ReactiveElement:w}),(G.reactiveElementVersions??=[]).push("2.1.2");var at=globalThis,gt=r=>r,O=at.trustedTypes,bt=O?O.createPolicy("lit-html",{createHTML:r=>r}):void 0,$t="$lit$",k=`lit$${Math.random().toFixed(9).slice(2)}$`,At="?"+k,Nt=`<${At}>`,L=document,I=()=>L.createComment(""),V=r=>r===null||typeof r!="object"&&typeof r!="function",lt=Array.isArray,qt=r=>lt(r)||typeof r?.[Symbol.iterator]=="function",et=`[ 	
\f\r]`,F=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,mt=/-->/g,xt=/>/g,T=RegExp(`>|${et}(?:([^\\s"'>=/]+)(${et}*=${et}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),vt=/'/g,_t=/"/g,Et=/^(?:script|style|textarea|title)$/i,ct=r=>(t,...e)=>({_$litType$:r,strings:t,values:e}),f=ct(1),Jt=ct(2),Ot=ct(3),M=Symbol.for("lit-noChange"),u=Symbol.for("lit-nothing"),yt=new WeakMap,P=L.createTreeWalker(L,129);function wt(r,t){if(!lt(r)||!r.hasOwnProperty("raw"))throw Error("invalid template strings array");return bt!==void 0?bt.createHTML(t):t}var zt=(r,t)=>{let e=r.length-1,s=[],i,o=t===2?"<svg>":t===3?"<math>":"",n=F;for(let p=0;p<e;p++){let l=r[p],g,m,d=-1,E=0;for(;E<l.length&&(n.lastIndex=E,m=n.exec(l),m!==null);)E=n.lastIndex,n===F?m[1]==="!--"?n=mt:m[1]!==void 0?n=xt:m[2]!==void 0?(Et.test(m[2])&&(i=RegExp("</"+m[2],"g")),n=T):m[3]!==void 0&&(n=T):n===T?m[0]===">"?(n=i??F,d=-1):m[1]===void 0?d=-2:(d=n.lastIndex-m[2].length,g=m[1],n=m[3]===void 0?T:m[3]==='"'?_t:vt):n===_t||n===vt?n=T:n===mt||n===xt?n=F:(n=T,i=void 0);let S=n===T&&r[p+1].startsWith("/>")?" ":"";o+=n===F?l+Nt:d>=0?(s.push(g),l.slice(0,d)+$t+l.slice(d)+k+S):l+k+(d===-2?p:S)}return[wt(r,o+(r[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},K=class r{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let o=0,n=0,p=t.length-1,l=this.parts,[g,m]=zt(t,e);if(this.el=r.createElement(g,s),P.currentNode=this.el.content,e===2||e===3){let d=this.el.content.firstChild;d.replaceWith(...d.childNodes)}for(;(i=P.nextNode())!==null&&l.length<p;){if(i.nodeType===1){if(i.hasAttributes())for(let d of i.getAttributeNames())if(d.endsWith($t)){let E=m[n++],S=i.getAttribute(d).split(k),Y=/([.?@])?(.*)/.exec(E);l.push({type:1,index:o,name:Y[2],strings:S,ctor:Y[1]==="."?it:Y[1]==="?"?rt:Y[1]==="@"?ot:R}),i.removeAttribute(d)}else d.startsWith(k)&&(l.push({type:6,index:o}),i.removeAttribute(d));if(Et.test(i.tagName)){let d=i.textContent.split(k),E=d.length-1;if(E>0){i.textContent=O?O.emptyScript:"";for(let S=0;S<E;S++)i.append(d[S],I()),P.nextNode(),l.push({type:2,index:++o});i.append(d[E],I())}}}else if(i.nodeType===8)if(i.data===At)l.push({type:2,index:o});else{let d=-1;for(;(d=i.data.indexOf(k,d+1))!==-1;)l.push({type:7,index:o}),d+=k.length-1}o++}}static createElement(t,e){let s=L.createElement("template");return s.innerHTML=t,s}};function H(r,t,e=r,s){if(t===M)return t;let i=s!==void 0?e._$Co?.[s]:e._$Cl,o=V(t)?void 0:t._$litDirective$;return i?.constructor!==o&&(i?._$AO?.(!1),o===void 0?i=void 0:(i=new o(r),i._$AT(r,e,s)),s!==void 0?(e._$Co??=[])[s]=i:e._$Cl=i),i!==void 0&&(t=H(r,i._$AS(r,t.values),i,s)),t}var st=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,i=(t?.creationScope??L).importNode(e,!0);P.currentNode=i;let o=P.nextNode(),n=0,p=0,l=s[0];for(;l!==void 0;){if(n===l.index){let g;l.type===2?g=new X(o,o.nextSibling,this,t):l.type===1?g=new l.ctor(o,l.name,l.strings,this,t):l.type===6&&(g=new nt(o,this,t)),this._$AV.push(g),l=s[++p]}n!==l?.index&&(o=P.nextNode(),n++)}return P.currentNode=L,i}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},X=class r{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,i){this.type=2,this._$AH=u,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=H(this,t,e),V(t)?t===u||t==null||t===""?(this._$AH!==u&&this._$AR(),this._$AH=u):t!==this._$AH&&t!==M&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):qt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==u&&V(this._$AH)?this._$AA.nextSibling.data=t:this.T(L.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,i=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=K.createElement(wt(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(e);else{let o=new st(i,this),n=o.u(this.options);o.p(e),this.T(n),this._$AH=o}}_$AC(t){let e=yt.get(t.strings);return e===void 0&&yt.set(t.strings,e=new K(t)),e}k(t){lt(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,i=0;for(let o of t)i===e.length?e.push(s=new r(this.O(I()),this.O(I()),this,this.options)):s=e[i],s._$AI(o),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=gt(t).nextSibling;gt(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},R=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,i,o){this.type=1,this._$AH=u,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=o,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=u}_$AI(t,e=this,s,i){let o=this.strings,n=!1;if(o===void 0)t=H(this,t,e,0),n=!V(t)||t!==this._$AH&&t!==M,n&&(this._$AH=t);else{let p=t,l,g;for(t=o[0],l=0;l<o.length-1;l++)g=H(this,p[s+l],e,l),g===M&&(g=this._$AH[l]),n||=!V(g)||g!==this._$AH[l],g===u?t=u:t!==u&&(t+=(g??"")+o[l+1]),this._$AH[l]=g}n&&!i&&this.j(t)}j(t){t===u?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},it=class extends R{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===u?void 0:t}},rt=class extends R{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==u)}},ot=class extends R{constructor(t,e,s,i,o){super(t,e,s,i,o),this.type=5}_$AI(t,e=this){if((t=H(this,t,e,0)??u)===M)return;let s=this._$AH,i=t===u&&s!==u||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,o=t!==u&&(s===u||i);i&&this.element.removeEventListener(this.name,this,s),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},nt=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){H(this,t)}};var jt=at.litHtmlPolyfillSupport;jt?.(K,X),(at.litHtmlVersions??=[]).push("3.3.3");var Ct=(r,t,e)=>{let s=e?.renderBefore??t,i=s._$litPart$;if(i===void 0){let o=e?.renderBefore??null;s._$litPart$=i=new X(t.insertBefore(I(),o),o,void 0,e??{})}return i._$AI(r),i};var pt=globalThis,b=class extends w{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=Ct(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return M}};b._$litElement$=!0,b.finalized=!0,pt.litElementHydrateSupport?.({LitElement:b});var Ft=pt.litElementPolyfillSupport;Ft?.({LitElement:b});(pt.litElementVersions??=[]).push("4.2.2");var _=r=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(r,t)}):customElements.define(r,t)};var It={attribute:!0,type:String,converter:j,reflect:!1,hasChanged:J},Vt=(r=It,t,e)=>{let{kind:s,metadata:i}=e,o=globalThis.litPropertyMetadata.get(i);if(o===void 0&&globalThis.litPropertyMetadata.set(i,o=new Map),s==="setter"&&((r=Object.create(r)).wrapped=!0),o.set(e.name,r),s==="accessor"){let{name:n}=e;return{set(p){let l=t.get.call(this);t.set.call(this,p),this.requestUpdate(n,l,r,!0,p)},init(p){return p!==void 0&&this.C(n,void 0,r,p),p}}}if(s==="setter"){let{name:n}=e;return function(p){let l=this[n];t.call(this,p),this.requestUpdate(n,l,r,!0,p)}}throw Error("Unsupported decorator location: "+s)};function c(r){return(t,e)=>typeof e=="object"?Vt(r,t,e):((s,i,o)=>{let n=i.hasOwnProperty(o);return i.constructor.createProperty(o,s),n?Object.getOwnPropertyDescriptor(i,o):void 0})(r,t,e)}function C(r){return c({...r,state:!0,attribute:!1})}var A=class extends b{constructor(){super(...arguments);this.open=!1;this.placeholder="Capture name (optional)";this.nameLabel="Capture name";this.viewportLabel="Visible area";this.regionLabel="Select area"}get captureName(){return this.input()?.value.trim()||""}set captureName(e){let s=this.input();s&&(s.value=e)}ensureCaptureName(e){let s=this.input();s&&!s.value.trim()&&(s.value=e)}reset(){this.captureName="",this.open=!1}firstUpdated(){this.renderRoot.querySelectorAll("[data-scope]").forEach(e=>{e.addEventListener("click",()=>{this.choose(e.dataset.scope)})})}render(){return f`
      <input
        type="text"
        maxlength="120"
        placeholder=${this.placeholder}
        aria-label=${this.nameLabel}
      >
      <button type="button" data-scope="viewport">${this.viewportLabel}</button>
      <button type="button" data-scope="region">${this.regionLabel}</button>
    `}input(){return this.renderRoot.querySelector("input")}choose(e){this.open=!1,this.dispatchEvent(new CustomEvent("synthesix-capture-choice",{bubbles:!0,composed:!0,detail:{scope:e,captureName:this.captureName}}))}};A.styles=x`
    ${$(y)}

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
  `,a([c({type:Boolean,reflect:!0})],A.prototype,"open",2),a([c()],A.prototype,"placeholder",2),a([c({attribute:"name-label"})],A.prototype,"nameLabel",2),a([c({attribute:"viewport-label"})],A.prototype,"viewportLabel",2),a([c({attribute:"region-label"})],A.prototype,"regionLabel",2),A=a([_("sx-overlay-capture-menu")],A);var U=class extends b{constructor(){super(...arguments);this.label=""}render(){return f`<button type="button"></button>`}updated(){let e=this.renderRoot.querySelector("button");if(!e)return;let s=this.getAttribute("label")||this.label;e.textContent=s,e.setAttribute("aria-label",s)}};U.styles=x`
    ${$(y)}

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
  `,a([c()],U.prototype,"label",2),U=a([_("sx-overlay-selection-trigger")],U);var D=class extends b{constructor(){super(...arguments);this.hint="Drag to select evidence \xB7 Esc to cancel";this._selecting=!1;this._startX=0;this._startY=0;this._onKeyDown=e=>{e.key==="Escape"&&(e.preventDefault(),this._emitCancel())};this._onPointerDown=e=>{e.preventDefault(),this._selecting=!0,this._startX=e.clientX,this._startY=e.clientY;let s=this._boxEl;s&&s.classList.add("is-active");try{this.setPointerCapture(e.pointerId)}catch{}};this._onPointerMove=e=>{if(!this._selecting)return;let s=this._boxEl;if(!s)return;let i=Math.min(this._startX,e.clientX),o=Math.min(this._startY,e.clientY);s.style.left=`${i}px`,s.style.top=`${o}px`,s.style.width=`${Math.abs(e.clientX-this._startX)}px`,s.style.height=`${Math.abs(e.clientY-this._startY)}px`};this._onPointerUp=e=>{if(!this._selecting)return;this._selecting=!1;let s=Math.min(this._startX,e.clientX),i=Math.min(this._startY,e.clientY),o=Math.abs(e.clientX-this._startX),n=Math.abs(e.clientY-this._startY);if(o<8||n<8){this._emitCancel();return}this.dispatchEvent(new CustomEvent("synthesix-region-selected",{bubbles:!0,composed:!0,detail:{x:s+window.scrollX,y:i+window.scrollY,width:o,height:n}}))}}connectedCallback(){super.connectedCallback(),document.addEventListener("keydown",this._onKeyDown,!0),this.addEventListener("pointerdown",this._onPointerDown),this.addEventListener("pointermove",this._onPointerMove),this.addEventListener("pointerup",this._onPointerUp)}disconnectedCallback(){document.removeEventListener("keydown",this._onKeyDown,!0),super.disconnectedCallback()}get _boxEl(){return this.renderRoot.querySelector(".box")}_emitCancel(){this.dispatchEvent(new CustomEvent("synthesix-region-cancel",{bubbles:!0,composed:!0}))}render(){return f`
      <div class="hint">${this.hint}</div>
      <div class="box"></div>
    `}};D.styles=x`
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
  `,a([c()],D.prototype,"hint",2),D=a([_("sx-overlay-selection-box")],D);var h=class extends b{constructor(){super(...arguments);this.baseTagsets=[];this.existingTags=[];this.tagsetProperties={};this.graphEntities=[];this.heading="Ajouter \xE0 l'enqu\xEAte";this.createHeading="Cr\xE9er une entit\xE9";this.typePlaceholder="Type d'entit\xE9...";this.createLabel="Cr\xE9er";this.attachHeading="Ajouter comme propri\xE9t\xE9";this.chooseEntityLabel="Choisir une entit\xE9...";this.propertyPlaceholder="Type de l'information";this.attachLabel="Rattacher";this._selectedText="";this._selectedEntityId="";this._triggerVisible=!1;this._menuVisible=!1;this._triggerLeft=0;this._triggerTop=0;this._menuLeft=0;this._menuTop=0;this._onDocMouseUp=e=>{e.composedPath().includes(this)||window.setTimeout(()=>this._showTrigger(),0)};this._onDocClick=e=>{e.composedPath().includes(this)||this._close()};this._onDocKeyDown=e=>{e.key==="Escape"&&this._close()};this._onTriggerClick=()=>{let s=this.renderRoot.querySelector(".trigger")?.getBoundingClientRect(),i=s?s.left:this._triggerLeft,o=s?s.bottom+6:this._triggerTop,n=this._selectionText()||this._selectedText;if(!n){this._close();return}this._selectedText=n,this._selectedEntityId="",this._menuLeft=Math.min(Math.max(i,8),Math.max(8,window.innerWidth-316)),this._menuTop=Math.min(Math.max(o,8),Math.max(8,window.innerHeight-320)),this._triggerVisible=!1,this._menuVisible=!0};this._onEntityChange=e=>{this._selectedEntityId=e.target.value};this._onCreate=()=>{let s=(this.renderRoot.querySelector(".type-input")?.value??"").trim();if(!s)return;let i=this._selectedText;this._close(),i&&this.dispatchEvent(new CustomEvent("synthesix-entity-create",{bubbles:!0,composed:!0,detail:{label:i,category:s}}))};this._onTypeKeydown=e=>{e.key==="Enter"&&(e.preventDefault(),this._onCreate())};this._onAttach=()=>{let e=this.renderRoot.querySelector("select"),s=this.renderRoot.querySelector(".prop-input"),i=e?.value??"",o=(s?.value??"").trim(),n=this._selectedText;this._close(),!(!n||!i||!o)&&this.dispatchEvent(new CustomEvent("synthesix-entity-attach",{bubbles:!0,composed:!0,detail:{label:n,entityId:i,propertyKey:o}}))};this._onPropKeydown=e=>{e.key==="Enter"&&(e.preventDefault(),this._onAttach())};this._stop=e=>e.stopPropagation()}connectedCallback(){super.connectedCallback(),document.addEventListener("mouseup",this._onDocMouseUp),document.addEventListener("click",this._onDocClick),document.addEventListener("keydown",this._onDocKeyDown,!0)}disconnectedCallback(){document.removeEventListener("mouseup",this._onDocMouseUp),document.removeEventListener("click",this._onDocClick),document.removeEventListener("keydown",this._onDocKeyDown,!0),super.disconnectedCallback()}_dedup(e){let s=new Set,i=[];for(let o of e){let n=String(o??"").trim(),p=n.toLowerCase();!n||s.has(p)||(s.add(p),i.push(n))}return i}get _typeSuggestions(){return this._dedup([...this.baseTagsets,...this.existingTags])}get _entities(){return this.graphEntities.filter(e=>String(e.id??"").trim())}get _propertySuggestions(){let e=this._entities.find(i=>String(i.id??"").trim()===String(this._selectedEntityId).trim());if(!e)return[];let s=[];for(let i of e.tags??[])s.push(...this.tagsetProperties[String(i??"").trim()]??[]);return s.push(...e.propertyKeys??[]),this._dedup(s)}_selectionText(){return String(window.getSelection()?.toString()??"").replace(/\s+/g," ").trim().slice(0,200)}_close(){this._menuVisible=!1,this._triggerVisible=!1,this._selectedEntityId="";let e=this.renderRoot.querySelector(".type-input"),s=this.renderRoot.querySelector(".prop-input"),i=this.renderRoot.querySelector("select");e&&(e.value=""),s&&(s.value=""),i&&(i.value="")}_showTrigger(){let e=this._selectionText(),s=window.getSelection();if(!e||!s||s.rangeCount===0){this._close();return}let i=s.getRangeAt(0).getBoundingClientRect();if(!i||!i.width&&!i.height){this._close();return}this._selectedText=e,this._triggerLeft=Math.min(Math.max(i.left,8),Math.max(8,window.innerWidth-150)),this._triggerTop=Math.max(8,i.top-38),this._menuVisible=!1,this._triggerVisible=!0}render(){let e=this._entities.length>0,s=`display:${this._triggerVisible?"block":"none"};left:${this._triggerLeft}px;top:${this._triggerTop}px;`,i=`left:${this._menuLeft}px;top:${this._menuTop}px;`;return f`
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
            ${this._typeSuggestions.map(o=>f`<option value=${o}></option>`)}
          </datalist>
        </div>
        <div class="attach">
          <div class="attach-title">${this.attachHeading}</div>
          <select ?disabled=${!e} @change=${this._onEntityChange}>
            <option value="">${this.chooseEntityLabel}</option>
            ${this._entities.map(o=>f`<option value=${o.id}>${o.label||o.id}</option>`)}
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
            ${this._propertySuggestions.map(o=>f`<option value=${o}></option>`)}
          </datalist>
          <button
            class="attach-btn"
            type="button"
            ?disabled=${!e}
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
  `,a([c({attribute:!1})],h.prototype,"baseTagsets",2),a([c({attribute:!1})],h.prototype,"existingTags",2),a([c({attribute:!1})],h.prototype,"tagsetProperties",2),a([c({attribute:!1})],h.prototype,"graphEntities",2),a([c()],h.prototype,"heading",2),a([c()],h.prototype,"createHeading",2),a([c({attribute:"type-placeholder"})],h.prototype,"typePlaceholder",2),a([c({attribute:"create-label"})],h.prototype,"createLabel",2),a([c({attribute:"attach-heading"})],h.prototype,"attachHeading",2),a([c({attribute:"choose-entity-label"})],h.prototype,"chooseEntityLabel",2),a([c({attribute:"property-placeholder"})],h.prototype,"propertyPlaceholder",2),a([c({attribute:"attach-label"})],h.prototype,"attachLabel",2),a([C()],h.prototype,"_selectedText",2),a([C()],h.prototype,"_selectedEntityId",2),a([C()],h.prototype,"_triggerVisible",2),a([C()],h.prototype,"_menuVisible",2),a([C()],h.prototype,"_triggerLeft",2),a([C()],h.prototype,"_triggerTop",2),a([C()],h.prototype,"_menuLeft",2),a([C()],h.prototype,"_menuTop",2),h=a([_("sx-overlay-entity-menu")],h);var v=class extends b{constructor(){super(...arguments);this.variant="primary";this.state="idle";this.label="";this.titleText="";this.ariaText="";this.icon="none";this.iconOnly=!1;this.disabled=!1}render(){return f`
      <button
        type="button"
      >
        ${this.renderIcon()}
        <span data-label></span>
      </button>
    `}updated(){let e=this.renderRoot.querySelector("button"),s=this.getAttribute("label")||this.label;if(!e)return;let i=e.querySelector("[data-label]");i&&(i.textContent=s),e.disabled=this.disabled||this.hasAttribute("disabled"),e.title=this.getAttribute("title-text")||this.titleText||s,e.setAttribute("aria-label",this.getAttribute("aria-text")||this.ariaText||s)}renderIcon(){return this.icon==="mark"?f`
        <svg viewBox="0 0 128 128" aria-hidden="true">
          ${Array.from({length:10},(e,s)=>f`
            <path
              d="M58 12 69 6l9 38-12 9-9-7z"
              transform="rotate(${s*36} 64 64)"
              fill=${s%2===0?"#FFFFFF":"#67E8F9"}
            ></path>
          `)}
          <circle cx="64" cy="64" r="14" fill="#FFFFFF"></circle>
        </svg>
      `:this.icon==="archive"?f`
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M5 3h11l3 3v15H5zM8 3v6h8V3M8 14h8M8 18h6"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linejoin="round"
          ></path>
        </svg>
      `:this.icon==="camera"?f`
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
      `:u}};v.styles=x`
    ${$(y)}

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
  `,a([c({reflect:!0})],v.prototype,"variant",2),a([c({reflect:!0})],v.prototype,"state",2),a([c()],v.prototype,"label",2),a([c({attribute:"title-text"})],v.prototype,"titleText",2),a([c({attribute:"aria-text"})],v.prototype,"ariaText",2),a([c({reflect:!0})],v.prototype,"icon",2),a([c({type:Boolean,attribute:"icon-only",reflect:!0})],v.prototype,"iconOnly",2),a([c({type:Boolean,reflect:!0})],v.prototype,"disabled",2),v=a([_("sx-overlay-action")],v);var N=class extends b{constructor(){super(...arguments);this.collapsed=!1}setCollapsed(e){this.collapsed!==e&&(this.collapsed=e,this.dispatchEvent(new CustomEvent("synthesix-overlay-toggle",{detail:{collapsed:this.collapsed},bubbles:!0,composed:!0})))}action(e){return this.querySelector(e)}setActionState(e,s,i,o){e&&(e.dataset.state=s,e.state=s,e.setAttribute("state",s),e.label=i,e.setAttribute("label",i),e.title=i,e.titleText=i,e.setAttribute("title-text",i),e.ariaText=i,e.setAttribute("aria-text",i),e.disabled=s===o,e.toggleAttribute("disabled",s===o))}setSaveButtonState(e,s){let i=this.action("[data-synthesix-save-page]");i&&(i.dataset.state=e,i.state=e,i.setAttribute("state",e),i.label=s,i.setAttribute("label",s),i.disabled=e==="saving",i.toggleAttribute("disabled",e==="saving"),i.titleText=i.title||s,i.setAttribute("title-text",i.title||s),i.ariaText=i.title||"Save page to active Synthesix investigation",i.setAttribute("aria-text",i.ariaText))}setCaptureState(e,s="Capture screenshot"){this.setActionState(this.action("[data-synthesix-capture]"),e,s,"capturing")}setArchiveState(e,s="Save page with HTML archive"){this.setActionState(this.action("[data-synthesix-archive]"),e,s,"archiving")}render(){return f`
      <div class="toolbar" data-synthesix-overlay-toolbar>
        <slot name="toolbar"></slot>
        <button
          class="toggle"
          type="button"
          title="Collapse Synthesix overlay"
          aria-label="Collapse Synthesix overlay"
          data-synthesix-overlay-collapse
          @click=${()=>this.setCollapsed(!0)}
        >
          &rsaquo;
        </button>
      </div>
      <div class="collapsed" data-synthesix-overlay-collapsed>
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
    `}};N.styles=x`
    ${$(y)}

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
      justify-content: flex-end;
      animation: sx-overlay-pop 140ms ease-out both;
    }

    :host([collapsed]) ::slotted(sx-overlay-capture-menu) {
      display: none !important;
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
  `,a([c({type:Boolean,reflect:!0})],N.prototype,"collapsed",2),N=a([_("sx-overlay-root")],N);window.SynthesixOverlay={tokensCss:y,version:"0.1.0"};var vs=y;})();
