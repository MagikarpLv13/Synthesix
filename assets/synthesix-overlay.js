"use strict";(()=>{var vt=Object.defineProperty;var At=Object.getOwnPropertyDescriptor;var f=(i,t,e,s)=>{for(var r=s>1?void 0:s?At(t,e):t,o=i.length-1,n;o>=0;o--)(n=i[o])&&(r=(s?n(t,e,r):n(r))||r);return s&&r&&vt(t,e,r),r};var P=`
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
`;var F=globalThis,j=F.ShadowRoot&&(F.ShadyCSS===void 0||F.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,V=Symbol(),it=new WeakMap,U=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==V)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(j&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=it.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&it.set(e,t))}return t}toString(){return this.cssText}},B=i=>new U(typeof i=="string"?i:i+"",void 0,V),W=(i,...t)=>{let e=i.length===1?i[0]:t.reduce((s,r,o)=>s+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+i[o+1],i[0]);return new U(e,i,V)},ot=(i,t)=>{if(j)i.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),r=F.litNonce;r!==void 0&&s.setAttribute("nonce",r),s.textContent=e.cssText,i.appendChild(s)}},K=j?i=>i:i=>i instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return B(e)})(i):i;var{is:xt,defineProperty:Et,getOwnPropertyDescriptor:St,getOwnPropertyNames:wt,getOwnPropertySymbols:Ct,getPrototypeOf:Pt}=Object,L=globalThis,nt=L.trustedTypes,Ut=nt?nt.emptyScript:"",Mt=L.reactiveElementPolyfillSupport,M=(i,t)=>i,T={toAttribute(i,t){switch(t){case Boolean:i=i?Ut:null;break;case Object:case Array:i=i==null?i:JSON.stringify(i)}return i},fromAttribute(i,t){let e=i;switch(t){case Boolean:e=i!==null;break;case Number:e=i===null?null:Number(i);break;case Object:case Array:try{e=JSON.parse(i)}catch{e=null}}return e}},q=(i,t)=>!xt(i,t),at={attribute:!0,type:String,converter:T,reflect:!1,useDefault:!1,hasChanged:q};Symbol.metadata??=Symbol("metadata"),L.litPropertyMetadata??=new WeakMap;var g=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=at){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),r=this.getPropertyDescriptor(t,s,e);r!==void 0&&Et(this.prototype,t,r)}}static getPropertyDescriptor(t,e,s){let{get:r,set:o}=St(this.prototype,t)??{get(){return this[e]},set(n){this[e]=n}};return{get:r,set(n){let h=r?.call(this);o?.call(this,n),this.requestUpdate(t,h,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??at}static _$Ei(){if(this.hasOwnProperty(M("elementProperties")))return;let t=Pt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(M("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(M("properties"))){let e=this.properties,s=[...wt(e),...Ct(e)];for(let r of s)this.createProperty(r,e[r])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,r]of e)this.elementProperties.set(s,r)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let r=this._$Eu(e,s);r!==void 0&&this._$Eh.set(r,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let r of s)e.unshift(K(r))}else t!==void 0&&e.push(K(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return ot(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),r=this.constructor._$Eu(t,s);if(r!==void 0&&s.reflect===!0){let o=(s.converter?.toAttribute!==void 0?s.converter:T).toAttribute(e,s.type);this._$Em=t,o==null?this.removeAttribute(r):this.setAttribute(r,o),this._$Em=null}}_$AK(t,e){let s=this.constructor,r=s._$Eh.get(t);if(r!==void 0&&this._$Em!==r){let o=s.getPropertyOptions(r),n=typeof o.converter=="function"?{fromAttribute:o.converter}:o.converter?.fromAttribute!==void 0?o.converter:T;this._$Em=r;let h=n.fromAttribute(e,o.type);this[r]=h??this._$Ej?.get(r)??h,this._$Em=null}}requestUpdate(t,e,s,r=!1,o){if(t!==void 0){let n=this.constructor;if(r===!1&&(o=this[t]),s??=n.getPropertyOptions(t),!((s.hasChanged??q)(o,e)||s.useDefault&&s.reflect&&o===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:r,wrapped:o},n){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),o!==!0||n!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),r===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[r,o]of this._$Ep)this[r]=o;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[r,o]of s){let{wrapped:n}=o,h=this[r];n!==!0||this._$AL.has(r)||h===void 0||this.C(r,void 0,o,h)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};g.elementStyles=[],g.shadowRootOptions={mode:"open"},g[M("elementProperties")]=new Map,g[M("finalized")]=new Map,Mt?.({ReactiveElement:g}),(L.reactiveElementVersions??=[]).push("2.1.2");var tt=globalThis,ht=i=>i,z=tt.trustedTypes,ct=z?z.createPolicy("lit-html",{createHTML:i=>i}):void 0,mt="$lit$",b=`lit$${Math.random().toFixed(9).slice(2)}$`,$t="?"+b,Tt=`<${$t}>`,x=document,O=()=>x.createComment(""),k=i=>i===null||typeof i!="object"&&typeof i!="function",et=Array.isArray,Rt=i=>et(i)||typeof i?.[Symbol.iterator]=="function",J=`[
\f\r]`,R=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,lt=/-->/g,dt=/>/g,v=RegExp(`>|${J}(?:([^\\s"'>=/]+)(${J}*=${J}*(?:[^
\f\r"'\`<>=]|("|')|))|$)`,"g"),pt=/'/g,ut=/"/g,gt=/^(?:script|style|textarea|title)$/i,st=i=>(t,...e)=>({_$litType$:i,strings:t,values:e}),C=st(1),It=st(2),Vt=st(3),E=Symbol.for("lit-noChange"),l=Symbol.for("lit-nothing"),ft=new WeakMap,A=x.createTreeWalker(x,129);function _t(i,t){if(!et(i)||!i.hasOwnProperty("raw"))throw Error("invalid template strings array");return ct!==void 0?ct.createHTML(t):t}var Ot=(i,t)=>{let e=i.length-1,s=[],r,o=t===2?"<svg>":t===3?"<math>":"",n=R;for(let h=0;h<e;h++){let a=i[h],d,p,c=-1,$=0;for(;$<a.length&&(n.lastIndex=$,p=n.exec(a),p!==null);)$=n.lastIndex,n===R?p[1]==="!--"?n=lt:p[1]!==void 0?n=dt:p[2]!==void 0?(gt.test(p[2])&&(r=RegExp("</"+p[2],"g")),n=v):p[3]!==void 0&&(n=v):n===v?p[0]===">"?(n=r??R,c=-1):p[1]===void 0?c=-2:(c=n.lastIndex-p[2].length,d=p[1],n=p[3]===void 0?v:p[3]==='"'?ut:pt):n===ut||n===pt?n=v:n===lt||n===dt?n=R:(n=v,r=void 0);let _=n===v&&i[h+1].startsWith("/>")?" ":"";o+=n===R?a+Tt:c>=0?(s.push(d),a.slice(0,c)+mt+a.slice(c)+b+_):a+b+(c===-2?h:_)}return[_t(i,o+(i[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},N=class i{constructor({strings:t,_$litType$:e},s){let r;this.parts=[];let o=0,n=0,h=t.length-1,a=this.parts,[d,p]=Ot(t,e);if(this.el=i.createElement(d,s),A.currentNode=this.el.content,e===2||e===3){let c=this.el.content.firstChild;c.replaceWith(...c.childNodes)}for(;(r=A.nextNode())!==null&&a.length<h;){if(r.nodeType===1){if(r.hasAttributes())for(let c of r.getAttributeNames())if(c.endsWith(mt)){let $=p[n++],_=r.getAttribute(c).split(b),D=/([.?@])?(.*)/.exec($);a.push({type:1,index:o,name:D[2],strings:_,ctor:D[1]==="."?Z:D[1]==="?"?G:D[1]==="@"?Q:w}),r.removeAttribute(c)}else c.startsWith(b)&&(a.push({type:6,index:o}),r.removeAttribute(c));if(gt.test(r.tagName)){let c=r.textContent.split(b),$=c.length-1;if($>0){r.textContent=z?z.emptyScript:"";for(let _=0;_<$;_++)r.append(c[_],O()),A.nextNode(),a.push({type:2,index:++o});r.append(c[$],O())}}}else if(r.nodeType===8)if(r.data===$t)a.push({type:2,index:o});else{let c=-1;for(;(c=r.data.indexOf(b,c+1))!==-1;)a.push({type:7,index:o}),c+=b.length-1}o++}}static createElement(t,e){let s=x.createElement("template");return s.innerHTML=t,s}};function S(i,t,e=i,s){if(t===E)return t;let r=s!==void 0?e._$Co?.[s]:e._$Cl,o=k(t)?void 0:t._$litDirective$;return r?.constructor!==o&&(r?._$AO?.(!1),o===void 0?r=void 0:(r=new o(i),r._$AT(i,e,s)),s!==void 0?(e._$Co??=[])[s]=r:e._$Cl=r),r!==void 0&&(t=S(i,r._$AS(i,t.values),r,s)),t}var Y=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,r=(t?.creationScope??x).importNode(e,!0);A.currentNode=r;let o=A.nextNode(),n=0,h=0,a=s[0];for(;a!==void 0;){if(n===a.index){let d;a.type===2?d=new H(o,o.nextSibling,this,t):a.type===1?d=new a.ctor(o,a.name,a.strings,this,t):a.type===6&&(d=new X(o,this,t)),this._$AV.push(d),a=s[++h]}n!==a?.index&&(o=A.nextNode(),n++)}return A.currentNode=x,r}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},H=class i{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,r){this.type=2,this._$AH=l,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=S(this,t,e),k(t)?t===l||t==null||t===""?(this._$AH!==l&&this._$AR(),this._$AH=l):t!==this._$AH&&t!==E&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Rt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==l&&k(this._$AH)?this._$AA.nextSibling.data=t:this.T(x.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,r=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=N.createElement(_t(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===r)this._$AH.p(e);else{let o=new Y(r,this),n=o.u(this.options);o.p(e),this.T(n),this._$AH=o}}_$AC(t){let e=ft.get(t.strings);return e===void 0&&ft.set(t.strings,e=new N(t)),e}k(t){et(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,r=0;for(let o of t)r===e.length?e.push(s=new i(this.O(O()),this.O(O()),this,this.options)):s=e[r],s._$AI(o),r++;r<e.length&&(this._$AR(s&&s._$AB.nextSibling,r),e.length=r)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=ht(t).nextSibling;ht(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},w=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,r,o){this.type=1,this._$AH=l,this._$AN=void 0,this.element=t,this.name=e,this._$AM=r,this.options=o,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=l}_$AI(t,e=this,s,r){let o=this.strings,n=!1;if(o===void 0)t=S(this,t,e,0),n=!k(t)||t!==this._$AH&&t!==E,n&&(this._$AH=t);else{let h=t,a,d;for(t=o[0],a=0;a<o.length-1;a++)d=S(this,h[s+a],e,a),d===E&&(d=this._$AH[a]),n||=!k(d)||d!==this._$AH[a],d===l?t=l:t!==l&&(t+=(d??"")+o[a+1]),this._$AH[a]=d}n&&!r&&this.j(t)}j(t){t===l?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},Z=class extends w{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===l?void 0:t}},G=class extends w{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==l)}},Q=class extends w{constructor(t,e,s,r,o){super(t,e,s,r,o),this.type=5}_$AI(t,e=this){if((t=S(this,t,e,0)??l)===E)return;let s=this._$AH,r=t===l&&s!==l||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,o=t!==l&&(s===l||r);r&&this.element.removeEventListener(this.name,this,s),o&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},X=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){S(this,t)}};var kt=tt.litHtmlPolyfillSupport;kt?.(N,H),(tt.litHtmlVersions??=[]).push("3.3.3");var bt=(i,t,e)=>{let s=e?.renderBefore??t,r=s._$litPart$;if(r===void 0){let o=e?.renderBefore??null;s._$litPart$=r=new H(t.insertBefore(O(),o),o,void 0,e??{})}return r._$AI(i),r};var rt=globalThis,y=class extends g{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=bt(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return E}};y._$litElement$=!0,y.finalized=!0,rt.litElementHydrateSupport?.({LitElement:y});var Nt=rt.litElementPolyfillSupport;Nt?.({LitElement:y});(rt.litElementVersions??=[]).push("4.2.2");var yt=i=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(i,t)}):customElements.define(i,t)};var Ht={attribute:!0,type:String,converter:T,reflect:!1,hasChanged:q},Dt=(i=Ht,t,e)=>{let{kind:s,metadata:r}=e,o=globalThis.litPropertyMetadata.get(r);if(o===void 0&&globalThis.litPropertyMetadata.set(r,o=new Map),s==="setter"&&((i=Object.create(i)).wrapped=!0),o.set(e.name,i),s==="accessor"){let{name:n}=e;return{set(h){let a=t.get.call(this);t.set.call(this,h),this.requestUpdate(n,a,i,!0,h)},init(h){return h!==void 0&&this.C(n,void 0,i,h),h}}}if(s==="setter"){let{name:n}=e;return function(h){let a=this[n];t.call(this,h),this.requestUpdate(n,a,i,!0,h)}}throw Error("Unsupported decorator location: "+s)};function m(i){return(t,e)=>typeof e=="object"?Dt(i,t,e):((s,r,o)=>{let n=r.hasOwnProperty(o);return r.constructor.createProperty(o,s),n?Object.getOwnPropertyDescriptor(r,o):void 0})(i,t,e)}var u=class extends y{constructor(){super(...arguments);this.variant="primary";this.state="idle";this.label="";this.titleText="";this.ariaText="";this.icon="none";this.iconOnly=!1;this.disabled=!1}render(){return C`
      <button
        type="button"
      >
        ${this.renderIcon()}
        <span data-label></span>
      </button>
    `}updated(){let e=this.renderRoot.querySelector("button"),s=this.getAttribute("label")||this.label;if(!e)return;let r=e.querySelector("[data-label]");r&&(r.textContent=s),e.disabled=this.disabled||this.hasAttribute("disabled"),e.title=this.getAttribute("title-text")||this.titleText||s,e.setAttribute("aria-label",this.getAttribute("aria-text")||this.ariaText||s)}renderIcon(){return this.icon==="mark"?C`
        <svg viewBox="0 0 128 128" aria-hidden="true">
          ${Array.from({length:10},(e,s)=>C`
            <path
              d="M58 12 69 6l9 38-12 9-9-7z"
              transform="rotate(${s*36} 64 64)"
              fill=${s%2===0?"#FFFFFF":"#67E8F9"}
            ></path>
          `)}
          <circle cx="64" cy="64" r="14" fill="#FFFFFF"></circle>
        </svg>
      `:this.icon==="archive"?C`
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M5 3h11l3 3v15H5zM8 3v6h8V3M8 14h8M8 18h6"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linejoin="round"
          ></path>
        </svg>
      `:this.icon==="camera"?C`
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
      `:l}};u.styles=W`
    ${B(P)}

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
  `,f([m({reflect:!0})],u.prototype,"variant",2),f([m({reflect:!0})],u.prototype,"state",2),f([m()],u.prototype,"label",2),f([m({attribute:"title-text"})],u.prototype,"titleText",2),f([m({attribute:"aria-text"})],u.prototype,"ariaText",2),f([m({reflect:!0})],u.prototype,"icon",2),f([m({type:Boolean,attribute:"icon-only",reflect:!0})],u.prototype,"iconOnly",2),f([m({type:Boolean,reflect:!0})],u.prototype,"disabled",2),u=f([yt("sx-overlay-action")],u);window.SynthesixOverlay={tokensCss:P,version:"0.1.0"};var Fe=P;})();
