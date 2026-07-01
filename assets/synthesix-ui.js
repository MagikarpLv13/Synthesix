"use strict";(()=>{var Ft=Object.defineProperty;var Kt=Object.getOwnPropertyDescriptor;var c=(o,e,t,s)=>{for(var r=s>1?void 0:s?Kt(e,t):e,i=o.length-1,n;i>=0;i--)(n=o[i])&&(r=(s?n(e,t,r):n(r))||r);return s&&r&&Ft(e,t,r),r};var st=globalThis,rt=st.ShadowRoot&&(st.ShadyCSS===void 0||st.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,ut=Symbol(),Et=new WeakMap,j=class{constructor(e,t,s){if(this._$cssResult$=!0,s!==ut)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(rt&&e===void 0){let s=t!==void 0&&t.length===1;s&&(e=Et.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),s&&Et.set(t,e))}return e}toString(){return this.cssText}},Mt=o=>new j(typeof o=="string"?o:o+"",void 0,ut),x=(o,...e)=>{let t=o.length===1?o[0]:e.reduce((s,r,i)=>s+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+o[i+1],o[0]);return new j(t,o,ut)},Ct=(o,e)=>{if(rt)o.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let s=document.createElement("style"),r=st.litNonce;r!==void 0&&s.setAttribute("nonce",r),s.textContent=t.cssText,o.appendChild(s)}},mt=rt?o=>o:o=>o instanceof CSSStyleSheet?(e=>{let t="";for(let s of e.cssRules)t+=s.cssText;return Mt(t)})(o):o;var{is:Yt,defineProperty:Wt,getOwnPropertyDescriptor:Zt,getOwnPropertyNames:Xt,getOwnPropertySymbols:Jt,getPrototypeOf:Qt}=Object,it=globalThis,Lt=it.trustedTypes,te=Lt?Lt.emptyScript:"",ee=it.reactiveElementPolyfillSupport,B=(o,e)=>o,q={toAttribute(o,e){switch(e){case Boolean:o=o?te:null;break;case Object:case Array:o=o==null?o:JSON.stringify(o)}return o},fromAttribute(o,e){let t=o;switch(e){case Boolean:t=o!==null;break;case Number:t=o===null?null:Number(o);break;case Object:case Array:try{t=JSON.parse(o)}catch{t=null}}return t}},ot=(o,e)=>!Yt(o,e),St={attribute:!0,type:String,converter:q,reflect:!1,useDefault:!1,hasChanged:ot};Symbol.metadata??=Symbol("metadata"),it.litPropertyMetadata??=new WeakMap;var E=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=St){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let s=Symbol(),r=this.getPropertyDescriptor(e,s,t);r!==void 0&&Wt(this.prototype,e,r)}}static getPropertyDescriptor(e,t,s){let{get:r,set:i}=Zt(this.prototype,e)??{get(){return this[t]},set(n){this[t]=n}};return{get:r,set(n){let l=r?.call(this);i?.call(this,n),this.requestUpdate(e,l,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??St}static _$Ei(){if(this.hasOwnProperty(B("elementProperties")))return;let e=Qt(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(B("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(B("properties"))){let t=this.properties,s=[...Xt(t),...Jt(t)];for(let r of s)this.createProperty(r,t[r])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[s,r]of t)this.elementProperties.set(s,r)}this._$Eh=new Map;for(let[t,s]of this.elementProperties){let r=this._$Eu(t,s);r!==void 0&&this._$Eh.set(r,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let s=new Set(e.flat(1/0).reverse());for(let r of s)t.unshift(mt(r))}else e!==void 0&&t.push(mt(e));return t}static _$Eu(e,t){let s=t.attribute;return s===!1?void 0:typeof s=="string"?s:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let s of t.keys())this.hasOwnProperty(s)&&(e.set(s,this[s]),delete this[s]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Ct(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,s){this._$AK(e,s)}_$ET(e,t){let s=this.constructor.elementProperties.get(e),r=this.constructor._$Eu(e,s);if(r!==void 0&&s.reflect===!0){let i=(s.converter?.toAttribute!==void 0?s.converter:q).toAttribute(t,s.type);this._$Em=e,i==null?this.removeAttribute(r):this.setAttribute(r,i),this._$Em=null}}_$AK(e,t){let s=this.constructor,r=s._$Eh.get(e);if(r!==void 0&&this._$Em!==r){let i=s.getPropertyOptions(r),n=typeof i.converter=="function"?{fromAttribute:i.converter}:i.converter?.fromAttribute!==void 0?i.converter:q;this._$Em=r;let l=n.fromAttribute(t,i.type);this[r]=l??this._$Ej?.get(r)??l,this._$Em=null}}requestUpdate(e,t,s,r=!1,i){if(e!==void 0){let n=this.constructor;if(r===!1&&(i=this[e]),s??=n.getPropertyOptions(e),!((s.hasChanged??ot)(i,t)||s.useDefault&&s.reflect&&i===this._$Ej?.get(e)&&!this.hasAttribute(n._$Eu(e,s))))return;this.C(e,t,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:s,reflect:r,wrapped:i},n){s&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,n??t??this[e]),i!==!0||n!==void 0)||(this._$AL.has(e)||(this.hasUpdated||s||(t=void 0),this._$AL.set(e,t)),r===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[r,i]of this._$Ep)this[r]=i;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[r,i]of s){let{wrapped:n}=i,l=this[r];n!==!0||this._$AL.has(r)||l===void 0||this.C(r,void 0,i,l)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(t)):this._$EM()}catch(s){throw e=!1,this._$EM(),s}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};E.elementStyles=[],E.shadowRootOptions={mode:"open"},E[B("elementProperties")]=new Map,E[B("finalized")]=new Map,ee?.({ReactiveElement:E}),(it.reactiveElementVersions??=[]).push("2.1.2");var _t=globalThis,Pt=o=>o,nt=_t.trustedTypes,Ot=nt?nt.createPolicy("lit-html",{createHTML:o=>o}):void 0,Dt="$lit$",M=`lit$${Math.random().toFixed(9).slice(2)}$`,Ut="?"+M,se=`<${Ut}>`,N=document,K=()=>N.createComment(""),Y=o=>o===null||typeof o!="object"&&typeof o!="function",$t=Array.isArray,re=o=>$t(o)||typeof o?.[Symbol.iterator]=="function",ft=`[ 	
\f\r]`,F=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Nt=/-->/g,Tt=/>/g,P=RegExp(`>|${ft}(?:([^\\s"'>=/]+)(${ft}*=${ft}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),zt=/'/g,Ht=/"/g,Gt=/^(?:script|style|textarea|title)$/i,wt=o=>(e,...t)=>({_$litType$:o,strings:e,values:t}),u=wt(1),ge=wt(2),ve=wt(3),T=Symbol.for("lit-noChange"),$=Symbol.for("lit-nothing"),Rt=new WeakMap,O=N.createTreeWalker(N,129);function Vt(o,e){if(!$t(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return Ot!==void 0?Ot.createHTML(e):e}var ie=(o,e)=>{let t=o.length-1,s=[],r,i=e===2?"<svg>":e===3?"<math>":"",n=F;for(let l=0;l<t;l++){let a=o[l],p,h,m=-1,b=0;for(;b<a.length&&(n.lastIndex=b,h=n.exec(a),h!==null);)b=n.lastIndex,n===F?h[1]==="!--"?n=Nt:h[1]!==void 0?n=Tt:h[2]!==void 0?(Gt.test(h[2])&&(r=RegExp("</"+h[2],"g")),n=P):h[3]!==void 0&&(n=P):n===P?h[0]===">"?(n=r??F,m=-1):h[1]===void 0?m=-2:(m=n.lastIndex-h[2].length,p=h[1],n=h[3]===void 0?P:h[3]==='"'?Ht:zt):n===Ht||n===zt?n=P:n===Nt||n===Tt?n=F:(n=P,r=void 0);let d=n===P&&o[l+1].startsWith("/>")?" ":"";i+=n===F?a+se:m>=0?(s.push(p),a.slice(0,m)+Dt+a.slice(m)+M+d):a+M+(m===-2?l:d)}return[Vt(o,i+(o[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),s]},W=class o{constructor({strings:e,_$litType$:t},s){let r;this.parts=[];let i=0,n=0,l=e.length-1,a=this.parts,[p,h]=ie(e,t);if(this.el=o.createElement(p,s),O.currentNode=this.el.content,t===2||t===3){let m=this.el.content.firstChild;m.replaceWith(...m.childNodes)}for(;(r=O.nextNode())!==null&&a.length<l;){if(r.nodeType===1){if(r.hasAttributes())for(let m of r.getAttributeNames())if(m.endsWith(Dt)){let b=h[n++],d=r.getAttribute(m).split(M),y=/([.?@])?(.*)/.exec(b);a.push({type:1,index:i,name:y[2],strings:d,ctor:y[1]==="."?vt:y[1]==="?"?bt:y[1]==="@"?xt:D}),r.removeAttribute(m)}else m.startsWith(M)&&(a.push({type:6,index:i}),r.removeAttribute(m));if(Gt.test(r.tagName)){let m=r.textContent.split(M),b=m.length-1;if(b>0){r.textContent=nt?nt.emptyScript:"";for(let d=0;d<b;d++)r.append(m[d],K()),O.nextNode(),a.push({type:2,index:++i});r.append(m[b],K())}}}else if(r.nodeType===8)if(r.data===Ut)a.push({type:2,index:i});else{let m=-1;for(;(m=r.data.indexOf(M,m+1))!==-1;)a.push({type:7,index:i}),m+=M.length-1}i++}}static createElement(e,t){let s=N.createElement("template");return s.innerHTML=e,s}};function R(o,e,t=o,s){if(e===T)return e;let r=s!==void 0?t._$Co?.[s]:t._$Cl,i=Y(e)?void 0:e._$litDirective$;return r?.constructor!==i&&(r?._$AO?.(!1),i===void 0?r=void 0:(r=new i(o),r._$AT(o,t,s)),s!==void 0?(t._$Co??=[])[s]=r:t._$Cl=r),r!==void 0&&(e=R(o,r._$AS(o,e.values),r,s)),e}var gt=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:s}=this._$AD,r=(e?.creationScope??N).importNode(t,!0);O.currentNode=r;let i=O.nextNode(),n=0,l=0,a=s[0];for(;a!==void 0;){if(n===a.index){let p;a.type===2?p=new Z(i,i.nextSibling,this,e):a.type===1?p=new a.ctor(i,a.name,a.strings,this,e):a.type===6&&(p=new yt(i,this,e)),this._$AV.push(p),a=s[++l]}n!==a?.index&&(i=O.nextNode(),n++)}return O.currentNode=N,r}p(e){let t=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(e,s,t),t+=s.strings.length-2):s._$AI(e[t])),t++}},Z=class o{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,s,r){this.type=2,this._$AH=$,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=s,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=R(this,e,t),Y(e)?e===$||e==null||e===""?(this._$AH!==$&&this._$AR(),this._$AH=$):e!==this._$AH&&e!==T&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):re(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==$&&Y(this._$AH)?this._$AA.nextSibling.data=e:this.T(N.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:s}=e,r=typeof s=="number"?this._$AC(e):(s.el===void 0&&(s.el=W.createElement(Vt(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===r)this._$AH.p(t);else{let i=new gt(r,this),n=i.u(this.options);i.p(t),this.T(n),this._$AH=i}}_$AC(e){let t=Rt.get(e.strings);return t===void 0&&Rt.set(e.strings,t=new W(e)),t}k(e){$t(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,s,r=0;for(let i of e)r===t.length?t.push(s=new o(this.O(K()),this.O(K()),this,this.options)):s=t[r],s._$AI(i),r++;r<t.length&&(this._$AR(s&&s._$AB.nextSibling,r),t.length=r)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let s=Pt(e).nextSibling;Pt(e).remove(),e=s}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},D=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,s,r,i){this.type=1,this._$AH=$,this._$AN=void 0,this.element=e,this.name=t,this._$AM=r,this.options=i,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=$}_$AI(e,t=this,s,r){let i=this.strings,n=!1;if(i===void 0)e=R(this,e,t,0),n=!Y(e)||e!==this._$AH&&e!==T,n&&(this._$AH=e);else{let l=e,a,p;for(e=i[0],a=0;a<i.length-1;a++)p=R(this,l[s+a],t,a),p===T&&(p=this._$AH[a]),n||=!Y(p)||p!==this._$AH[a],p===$?e=$:e!==$&&(e+=(p??"")+i[a+1]),this._$AH[a]=p}n&&!r&&this.j(e)}j(e){e===$?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},vt=class extends D{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===$?void 0:e}},bt=class extends D{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==$)}},xt=class extends D{constructor(e,t,s,r,i){super(e,t,s,r,i),this.type=5}_$AI(e,t=this){if((e=R(this,e,t,0)??$)===T)return;let s=this._$AH,r=e===$&&s!==$||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,i=e!==$&&(s===$||r);r&&this.element.removeEventListener(this.name,this,s),i&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},yt=class{constructor(e,t,s){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(e){R(this,e)}};var oe=_t.litHtmlPolyfillSupport;oe?.(W,Z),(_t.litHtmlVersions??=[]).push("3.3.3");var It=(o,e,t)=>{let s=t?.renderBefore??e,r=s._$litPart$;if(r===void 0){let i=t?.renderBefore??null;s._$litPart$=r=new Z(e.insertBefore(K(),i),i,void 0,t??{})}return r._$AI(o),r};var kt=globalThis,f=class extends E{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=It(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return T}};f._$litElement$=!0,f.finalized=!0,kt.litElementHydrateSupport?.({LitElement:f});var ne=kt.litElementPolyfillSupport;ne?.({LitElement:f});(kt.litElementVersions??=[]).push("4.2.2");var g=o=>(e,t)=>{t!==void 0?t.addInitializer(()=>{customElements.define(o,e)}):customElements.define(o,e)};var ae={attribute:!0,type:String,converter:q,reflect:!1,hasChanged:ot},le=(o=ae,e,t)=>{let{kind:s,metadata:r}=t,i=globalThis.litPropertyMetadata.get(r);if(i===void 0&&globalThis.litPropertyMetadata.set(r,i=new Map),s==="setter"&&((o=Object.create(o)).wrapped=!0),i.set(t.name,o),s==="accessor"){let{name:n}=t;return{set(l){let a=e.get.call(this);e.set.call(this,l),this.requestUpdate(n,a,o,!0,l)},init(l){return l!==void 0&&this.C(n,void 0,o,l),l}}}if(s==="setter"){let{name:n}=t;return function(l){let a=this[n];e.call(this,l),this.requestUpdate(n,a,o,!0,l)}}throw Error("Unsupported decorator location: "+s)};function v(o){return(e,t)=>typeof t=="object"?le(o,e,t):((s,r,i)=>{let n=r.hasOwnProperty(i);return r.constructor.createProperty(i,s),n?Object.getOwnPropertyDescriptor(r,i):void 0})(o,e,t)}function at(o){return v({...o,state:!0,attribute:!1})}var U=class extends f{constructor(){super(...arguments);this.tone="neutral"}render(){return u`<span class="chip"><slot></slot></span>`}};U.styles=x`
    :host {
      display: inline-flex;
    }
    .chip {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font: 12px/1 system-ui, Arial, sans-serif;
      padding: 4px 9px;
      border-radius: var(--radius-sm, 6px);
      background: var(--surface-2, #f1f5f9);
      color: var(--muted, #64748b);
      border: 1px solid transparent;
      white-space: nowrap;
    }
    :host([tone="info"]) .chip {
      background: var(--accent-soft, #dbeafe);
      color: var(--accent-ink, #1d4ed8);
    }
    :host([tone="success"]) .chip {
      background: var(--success-soft, #dcfce7);
      color: var(--success-ink, #166534);
    }
    :host([tone="engine"]) .chip {
      color: var(--text, #0f172a);
      border-color: var(--line, #cbd5e1);
    }
    :host([tone="muted"]) .chip {
      background: transparent;
    }
  `,c([v({reflect:!0})],U.prototype,"tone",2),U=c([g("sx-chip")],U);var z=class extends f{constructor(){super(...arguments);this.accent="none";this.triage=!1}willUpdate(t){t.has("triage")&&(this.triage?(this.setAttribute("data-triage-item",""),this.hasAttribute("tabindex")||this.setAttribute("tabindex","0")):this.removeAttribute("data-triage-item"))}render(){return u`
      <article class="card" part="card">
        <div class="source" part="source">
          <slot name="favicon"></slot>
          <slot name="source"></slot>
          <span class="meta" part="meta"><slot name="meta"></slot></span>
        </div>
        <div class="title" part="title"><slot name="title"></slot></div>
        <div class="breadcrumb" part="breadcrumb"><slot name="domain"></slot></div>
        <div class="snippet" part="snippet"><slot name="snippet"></slot></div>
        <div class="extra" part="extra"><slot name="extra"></slot></div>
        <slot name="actions"></slot>
      </article>
    `}};z.styles=x`
    :host {
      display: block;
      max-width: 680px;
      margin-bottom: 8px;
      outline: none;
    }

    .card {
      padding: 6px 8px;
      border-radius: var(--radius-sm, 6px);
      font-family: var(--font-body, system-ui, Arial, sans-serif);
      transition: background-color 120ms ease;
    }

    :host(:hover) .card {
      background: var(--surface-2, #f1f5f9);
    }

    :host(:focus-visible) .card,
    :host(:focus) .card {
      background: var(--surface-2, #f1f5f9);
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }

    .source {
      display: flex;
      align-items: center;
      gap: var(--space-2, 8px);
      min-width: 0;
    }

    .meta {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 6px;
      margin-left: auto;
      flex: 0 0 auto;
    }

    .title {
      margin: 3px 0 0;
      line-height: 1.3;
    }

    .breadcrumb {
      margin: 1px 0 0;
    }

    .snippet {
      margin: 3px 0 0;
    }

    .extra {
      display: contents;
    }

    ::slotted([slot="favicon"]) {
      flex: 0 0 auto;
      display: inline-grid;
      place-items: center;
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: var(--surface-2, #f1f5f9);
      border: 1px solid var(--line, #cbd5e1);
      color: var(--muted, #64748b);
      font: 700 11px system-ui, Arial, sans-serif;
    }

    ::slotted([slot="source"]) {
      min-width: 0;
      overflow: hidden;
      color: var(--text, #0f172a);
      font-size: 13px;
      line-height: 1.3;
      white-space: nowrap;
      text-overflow: ellipsis;
    }

    ::slotted([slot="title"]) {
      color: var(--accent, #2563eb);
      font-size: 18px;
      font-weight: 400;
      overflow-wrap: anywhere;
      text-decoration: none;
    }

    ::slotted([slot="title"]:hover) {
      text-decoration: underline;
    }

    ::slotted([slot="domain"]) {
      display: block;
      min-width: 0;
      overflow: hidden;
      color: var(--muted, #64748b);
      font-size: 12px;
      line-height: 1.3;
      white-space: nowrap;
      text-overflow: ellipsis;
    }

    ::slotted([slot="snippet"]) {
      margin: 0;
      color: var(--muted, #64748b);
      font-size: 14px;
      line-height: 1.45;
      overflow-wrap: anywhere;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
  `,c([v({reflect:!0})],z.prototype,"accent",2),c([v({type:Boolean,reflect:!0})],z.prototype,"triage",2),z=c([g("sx-result-card")],z);var H=class extends f{constructor(){super(...arguments);this.level="none";this.tip=!1}updated(t){t.has("tip")&&(this.tabIndex=this.tip?0:-1)}render(){let t=u`<span class="value" part="value"><slot></slot></span>`;return this.tip?u`
      ${t}
      <span class="tooltip" part="tooltip" role="tooltip">
        <slot name="breakdown"></slot>
        <slot name="note"></slot>
      </span>
    `:t}};H.styles=x`
    :host {
      display: inline-flex;
      align-items: center;
    }

    :host([tip]) {
      position: relative;
      cursor: help;
      outline: none;
    }

    .value {
      display: inline-block;
      font-variant-numeric: tabular-nums;
      font-weight: 600;
      font-size: 13px;
      padding: 3px 9px;
      border-radius: var(--radius-sm, 6px);
      background: var(--surface-2, #f1f5f9);
      color: var(--text, #0f172a);
      border: 1px solid var(--line, #cbd5e1);
    }

    :host([level="strong"]) .value {
      background: var(--success-soft, #dcfce7);
      color: var(--success-ink, #166534);
      border-color: transparent;
    }

    :host([level="good"]) .value {
      background: var(--accent-soft, #dbeafe);
      color: var(--accent-ink, #1d4ed8);
      border-color: transparent;
    }

    :host([level="moderate"]) .value {
      background: var(--warning-soft, #fef3c7);
      color: var(--warning-ink, #92400e);
      border-color: transparent;
    }

    :host([tip]:focus-visible) .value {
      outline: none;
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }

    .tooltip {
      position: absolute;
      z-index: 40;
      top: calc(100% + 6px);
      right: 0;
      width: max-content;
      max-width: 380px;
      padding: 8px 10px;
      text-align: left;
      background: var(--surface, #ffffff);
      border: 1px solid var(--line, #cbd5e1);
      border-radius: var(--radius-sm, 6px);
      box-shadow: var(--shadow-soft, 0 8px 24px rgba(15, 23, 42, 0.12));
      opacity: 0;
      visibility: hidden;
      transform: translateY(-3px);
      transition: opacity 120ms ease, transform 120ms ease,
        visibility 0s linear 120ms;
      pointer-events: none;
    }

    :host([tip]:hover) .tooltip,
    :host([tip]:focus) .tooltip,
    :host([tip]:focus-within) .tooltip {
      opacity: 1;
      visibility: visible;
      transform: translateY(0);
      transition: opacity 120ms ease, transform 120ms ease;
    }
  `,c([v({reflect:!0})],H.prototype,"level",2),c([v({type:Boolean,reflect:!0})],H.prototype,"tip",2),H=c([g("sx-score")],H);var C=class extends f{constructor(){super(...arguments);this.tone="muted";this.removable=!1;this.removeLabel="Remove"}_remove(){this.dispatchEvent(new CustomEvent("sx-tag-remove",{bubbles:!0,composed:!0}))}render(){return u`<span class="tag" part="tag">
      <slot></slot>
      ${this.removable?u`<button
            class="remove"
            part="remove"
            type="button"
            aria-label=${this.removeLabel}
            @click=${this._remove}
          >
            &times;
          </button>`:null}
    </span>`}};C.styles=x`
    :host {
      display: inline-flex;
    }
    .tag {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font: 12px/1 system-ui, Arial, sans-serif;
      padding: 3px 8px;
      border-radius: var(--radius-sm, 6px);
      background: var(--surface-2, #f1f5f9);
      color: var(--muted, #64748b);
      border: 1px solid transparent;
      white-space: nowrap;
    }
    :host([tone="neutral"]) .tag {
      color: var(--text, #0f172a);
    }
    :host([tone="info"]) .tag {
      background: var(--accent-soft, #dbeafe);
      color: var(--accent-ink, #1d4ed8);
    }
    :host([tone="success"]) .tag {
      background: var(--success-soft, #dcfce7);
      color: var(--success-ink, #166534);
    }
    :host([tone="engine"]) .tag {
      background: var(--surface-2, #f1f5f9);
      color: var(--text, #0f172a);
      border-color: var(--line, #cbd5e1);
    }
    .remove {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 14px;
      height: 14px;
      margin-right: -2px;
      padding: 0;
      border: none;
      border-radius: 50%;
      background: transparent;
      color: inherit;
      font: inherit;
      line-height: 1;
      cursor: pointer;
      opacity: 0.7;
    }
    .remove:hover {
      opacity: 1;
      background: color-mix(in srgb, currentColor 18%, transparent);
    }
    .remove:focus-visible {
      outline: none;
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }
  `,c([v({reflect:!0})],C.prototype,"tone",2),c([v({type:Boolean,reflect:!0})],C.prototype,"removable",2),c([v({attribute:"remove-label"})],C.prototype,"removeLabel",2),C=c([g("sx-tag")],C);var X=class extends f{render(){return u`<span class="provenance" part="provenance">
      <slot name="icon"></slot>
      <span class="label" part="label"><slot name="label"></slot></span>
      <span class="detail" part="detail"><slot></slot></span>
    </span>`}};X.styles=x`
    :host {
      display: inline-flex;
    }
    .provenance {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 12px;
      color: var(--muted, #64748b);
      min-width: 0;
    }
    .detail {
      color: var(--text, #0f172a);
      overflow-wrap: anywhere;
    }
    ::slotted([slot="icon"]) {
      width: 0.95em;
      height: 0.95em;
      flex: 0 0 auto;
    }
  `,X=c([g("sx-provenance")],X);var G=class extends f{constructor(){super(...arguments);this.status="pending"}render(){return u`<span
      class="badge"
      part="badge"
      role="status"
      aria-live="polite"
    >
      <slot></slot>
    </span>`}};G.styles=x`
    :host {
      display: inline-flex;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 14px;
      font-size: 12px;
      font-weight: 700;
      color: var(--muted, #64748b);
    }
    :host([status="verified"]) .badge {
      color: var(--success-ink, #166534);
    }
    :host([status="error"]) .badge {
      color: var(--danger, #dc2626);
    }
  `,c([v({reflect:!0})],G.prototype,"status",2),G=c([g("sx-evidence-badge")],G);var L=class extends f{constructor(){super(...arguments);this.kind="";this.confidence="";this.status="candidate"}_onOptionalSlot(t){let s=t.target,r=s.parentElement;if(!r)return;let i=s.assignedNodes({flatten:!0}).some(n=>n.nodeType===Node.ELEMENT_NODE||(n.textContent??"").trim().length>0);r.hidden=!i}render(){return u`
      <article class="entity" part="entity">
        <div class="head" part="head">
          <span class="kind" part="kind">${this.kind}</span>
          ${this.confidence?u`<span class="confidence" part="confidence">${this.confidence}</span>`:null}
          <span class="actions" part="actions"><slot name="actions"></slot></span>
        </div>
        <div class="value" part="value"><slot></slot></div>
        <div class="meta" part="meta" hidden>
          <slot name="meta" @slotchange=${this._onOptionalSlot}></slot>
        </div>
        <div class="properties" part="properties" hidden>
          <slot name="properties" @slotchange=${this._onOptionalSlot}></slot>
        </div>
      </article>
    `}};L.styles=x`
    :host {
      display: block;
    }
    .entity {
      padding: 12px 14px;
      border: 1px solid var(--line, #cbd5e1);
      border-left: 4px solid var(--line, #cbd5e1);
      border-radius: var(--radius-md, 8px);
      background: var(--surface, #ffffff);
      color: var(--text, #0f172a);
    }
    :host([status="confirmed"]) .entity {
      border-left-color: var(--secondary, #06b6d4);
    }
    :host([status="rejected"]) .entity {
      opacity: 0.65;
    }
    .head {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }
    .kind {
      color: var(--secondary, #06b6d4);
      font-size: 12px;
      font-weight: 700;
      text-transform: capitalize;
    }
    .confidence {
      color: var(--muted, #64748b);
      font-size: 11px;
    }
    .actions {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin-left: auto;
    }
    .value {
      margin-top: 4px;
      font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
      font-size: 13px;
      color: var(--text, #0f172a);
      overflow-wrap: anywhere;
    }
    .meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .meta[hidden],
    .properties[hidden] {
      display: none;
    }
    .meta:not([hidden]),
    .properties:not([hidden]) {
      margin-top: 8px;
    }
    .properties {
      display: grid;
      gap: 4px;
    }
  `,c([v()],L.prototype,"kind",2),c([v()],L.prototype,"confidence",2),c([v({reflect:!0})],L.prototype,"status",2),L=c([g("sx-entity")],L);var J="http://www.w3.org/2000/svg",jt={personne:"#38bdf8",entreprise:"#a78bfa",organisation:"#a78bfa",lieu:"#34d399",adresse:"#34d399",\u00E9v\u00E9nement:"#fbbf24",evenement:"#fbbf24",document:"#f472b6",identifiant:"#f59e0b"},Bt=["#38bdf8","#a78bfa","#34d399","#fbbf24","#f472b6","#22d3ee","#c084fc"];function ce(o){let e=(o??"").trim().toLowerCase();if(e&&jt[e])return jt[e];if(!e)return"#94a3b8";let t=0;for(let s=0;s<e.length;s+=1)t=t*31+e.charCodeAt(s)|0;return Bt[Math.abs(t)%Bt.length]}var S=class extends f{constructor(){super(...arguments);this.data=null;this.storageKey="";this._empty=!1;this._particles=[];this._links=[];this._byId=new Map;this._legend=[];this._k=1;this._tx=0;this._ty=0;this._width=0;this._height=0;this._resizeObs=null;this._laidOut=!1;this._mode="idle";this._dragParticle=null;this._startX=0;this._startY=0;this._moved=!1;this._activeId=null;this._onWheel=t=>{t.preventDefault();let s=this.getBoundingClientRect(),r=t.deltaY<0?1.12:1/1.12;this._zoomBy(r,t.clientX-s.left,t.clientY-s.top)};this._onPointerDown=t=>{if(t.button!==0)return;let r=t.target.closest(".node");if(this._startX=t.clientX,this._startY=t.clientY,this._moved=!1,this._svg?.setPointerCapture(t.pointerId),r?.dataset.id){let i=this._byId.get(r.dataset.id);i&&(this._mode="node",this._dragParticle=i,i.fixed=!0)}else this._mode="pan",this._svg?.classList.add("is-panning");window.addEventListener("pointermove",this._onPointerMove),window.addEventListener("pointerup",this._onPointerUp)};this._onPointerMove=t=>{let s=t.clientX-this._startX,r=t.clientY-this._startY;if(!this._moved&&Math.hypot(s,r)>4&&(this._moved=!0),this._mode==="pan")this._tx+=t.movementX,this._ty+=t.movementY,this._draw();else if(this._mode==="node"&&this._dragParticle){let i=this._toWorld(t.clientX,t.clientY);this._dragParticle.x=i.x,this._dragParticle.y=i.y,this._draw()}};this._onPointerUp=t=>{if(window.removeEventListener("pointermove",this._onPointerMove),window.removeEventListener("pointerup",this._onPointerUp),this._svg?.classList.remove("is-panning"),this._mode==="node"&&this._dragParticle){let s=this._dragParticle;s.fixed=!1,this._moved?this._saveLayout():this._select(s.node.id)}this._mode="idle",this._dragParticle=null}}get _svg(){return this.renderRoot.querySelector(".stage")}get _viewport(){return this.renderRoot.querySelector(".viewport")}get _edgesG(){return this.renderRoot.querySelector(".edges")}get _nodesG(){return this.renderRoot.querySelector(".nodes")}connectedCallback(){super.connectedCallback(),this.data||(this.data=this._readInlineData())}disconnectedCallback(){super.disconnectedCallback(),this._resizeObs?.disconnect(),this._resizeObs=null}firstUpdated(){let t=this._svg;t&&(t.addEventListener("wheel",this._onWheel,{passive:!1}),t.addEventListener("pointerdown",this._onPointerDown)),this._resizeObs=new ResizeObserver(s=>{let r=s[0]?.contentRect;r&&(this._width=r.width,this._height=r.height,!this._laidOut&&this._width>0&&this._height>0&&this._build())}),this._resizeObs.observe(this)}updated(t){t.has("data")&&(this._laidOut=!1,this._width>0&&this._height>0&&this._build())}_readInlineData(){let t=this.querySelector("script[data-graph-data]");if(!t?.textContent)return null;try{let s=JSON.parse(t.textContent);if(Array.isArray(s.nodes))return s}catch{}return null}_build(){let t=this._edgesG,s=this._nodesG;if(!t||!s)return;this.data||(this.data=this._readInlineData()),t.replaceChildren(),s.replaceChildren(),this._particles=[],this._links=[],this._byId.clear();let r=this.data?.nodes??[],i=this.data?.edges??[];if(this._empty=r.length===0,this._empty){this._laidOut=!0;return}let n=new Map,l=[],a=new Set(r.map(d=>d.id));for(let d of i)d.source!==d.target&&(!a.has(d.source)||!a.has(d.target)||(l.push(d),n.set(d.source,(n.get(d.source)??0)+1),n.set(d.target,(n.get(d.target)??0)+1)));let p=this._loadLayout(),h=r.length,m=50*Math.sqrt(h)+60,b=new Map;r.forEach((d,y)=>{let k=n.get(d.id)??0,w=ce(d.category);d.category&&b.set(d.category,w);let _=p?.[d.id],V=Math.random()*Math.PI*2,At=Math.sqrt(Math.random())*m,I={node:d,x:_?_.x:Math.cos(V)*At,y:_?_.y:Math.sin(V)*At,vx:0,vy:0,r:8+Math.min(14,k*2.2),degree:k,fixed:!!_,el:this._makeNode(d,w,k),circle:null};I.circle=I.el.querySelector("circle"),this._particles.push(I),this._byId.set(d.id,I),s.appendChild(I.el)});for(let d of l){let y=this._byId.get(d.source),k=this._byId.get(d.target);if(!y||!k)continue;let w=document.createElementNS(J,"line");w.setAttribute("class","edge"),w.setAttribute("marker-end","url(#sx-graph-arrow)"),t.appendChild(w);let _=null;d.label&&(_=document.createElementNS(J,"text"),_.setAttribute("class","edge-label"),_.setAttribute("text-anchor","middle"),_.textContent=d.label,t.appendChild(_)),this._links.push({edge:d,a:y,b:k,line:w,label:_})}this._legend=[...b.entries()].map(([d,y])=>({label:d,color:y})),this._laidOut=!0,this._settle();for(let d of this._particles)d.fixed=!1;this._saveLayout(),this.fit(),this.requestUpdate()}_loadLayout(){if(!this.storageKey)return null;try{let t=localStorage.getItem(this.storageKey);if(!t)return null;let s=JSON.parse(t);return s&&typeof s=="object"?s:null}catch{return null}}_saveLayout(){if(!(!this.storageKey||this._particles.length===0))try{let t={};for(let s of this._particles)t[s.node.id]={x:Math.round(s.x),y:Math.round(s.y)};localStorage.setItem(this.storageKey,JSON.stringify(t))}catch{}}reorganize(){if(this.storageKey)try{localStorage.removeItem(this.storageKey)}catch{}this._build()}_makeNode(t,s,r){let i=document.createElementNS(J,"g");i.setAttribute("class","node"),i.setAttribute("tabindex","0"),i.setAttribute("role","button"),i.setAttribute("aria-label",`${t.label}${t.category?` (${t.category})`:""}`),i.dataset.id=t.id;let n=document.createElementNS(J,"circle"),l=8+Math.min(14,r*2.2);n.setAttribute("r",String(l)),n.setAttribute("fill",s),i.appendChild(n);let a=document.createElementNS(J,"text");a.setAttribute("text-anchor","middle"),a.setAttribute("dy",String(-l-6));let p=t.label.length>28?`${t.label.slice(0,27)}\u2026`:t.label;return a.textContent=p,i.appendChild(a),i.addEventListener("keydown",h=>{(h.key==="Enter"||h.key===" ")&&(h.preventDefault(),this._select(t.id))}),i.addEventListener("pointerenter",()=>this._highlight(t.id)),i.addEventListener("pointerleave",()=>this._highlight(null)),i.addEventListener("focus",()=>this._highlight(t.id)),i.addEventListener("blur",()=>this._highlight(null)),i}_step(t){let s=this._particles,r=s.length,i=7e3,n=.012;for(let a=0;a<r;a+=1){let p=s[a];for(let h=a+1;h<r;h+=1){let m=s[h],b=p.x-m.x,d=p.y-m.y,y=b*b+d*d;y<.01&&(b=Math.random()-.5,d=Math.random()-.5,y=b*b+d*d);let k=Math.sqrt(y),w=Math.min(i/y,90),_=b/k*w,V=d/k*w;p.vx+=_,p.vy+=V,m.vx-=_,m.vy-=V}p.vx-=p.x*n,p.vy-=p.y*n}for(let a of this._links){let{a:p,b:h}=a,m=h.x-p.x,b=h.y-p.y,d=Math.sqrt(m*m+b*b)||1,y=150+p.r+h.r,k=(d-y)*.06,w=m/d*k,_=b/d*k;p.vx+=w,p.vy+=_,h.vx-=w,h.vy-=_}let l=.85;for(let a of s){if(a.fixed){a.vx=0,a.vy=0;continue}a.vx*=l,a.vy*=l,a.x+=a.vx*t,a.y+=a.vy*t}}_settle(){let t=1;for(let s=0;s<450&&t>.004;s+=1)this._step(t),t*=.985;this._draw()}_draw(){let t=this._viewport;t&&t.setAttribute("transform",`translate(${this._tx} ${this._ty}) scale(${this._k})`);for(let s of this._particles)s.el.setAttribute("transform",`translate(${s.x} ${s.y})`);for(let s of this._links){let{a:r,b:i,line:n,label:l}=s,a=i.x-r.x,p=i.y-r.y,h=Math.sqrt(a*a+p*p)||1,m=a/h,b=p/h;n.setAttribute("x1",String(r.x+m*r.r)),n.setAttribute("y1",String(r.y+b*r.r)),n.setAttribute("x2",String(i.x-m*(i.r+6))),n.setAttribute("y2",String(i.y-b*(i.r+6))),l&&(l.setAttribute("x",String((r.x+i.x)/2)),l.setAttribute("y",String((r.y+i.y)/2)))}}fit(){if(this._particles.length===0||this._width===0)return;let t=1/0,s=1/0,r=-1/0,i=-1/0;for(let h of this._particles)t=Math.min(t,h.x-h.r),s=Math.min(s,h.y-h.r),r=Math.max(r,h.x+h.r),i=Math.max(i,h.y+h.r);let n=48,l=r-t||1,a=i-s||1,p=Math.min((this._width-n*2)/l,(this._height-n*2)/a,1.6);this._k=Math.max(.1,p),this._tx=this._width/2-(t+r)/2*this._k,this._ty=this._height/2-(s+i)/2*this._k,this._draw()}_zoomBy(t,s,r){let i=s??this._width/2,n=r??this._height/2,l=Math.max(.1,Math.min(4,this._k*t));this._tx=i-(i-this._tx)*l/this._k,this._ty=n-(n-this._ty)*l/this._k,this._k=l,this._draw()}_toWorld(t,s){let r=this.getBoundingClientRect(),i=t-r.left,n=s-r.top;return{x:(i-this._tx)/this._k,y:(n-this._ty)/this._k}}_select(t){this.dispatchEvent(new CustomEvent("sx-entity-select",{detail:{id:t},bubbles:!0,composed:!0}))}_highlight(t){if(t===this._activeId)return;this._activeId=t;let s=this._svg;if(!s)return;if(!t){s.classList.remove("is-hovering");for(let i of this._particles)i.el.classList.remove("is-active");for(let i of this._links)i.line.classList.remove("is-active"),i.label?.classList.remove("is-active");return}let r=new Set([t]);for(let i of this._links){let n=i.a.node.id===t||i.b.node.id===t;i.line.classList.toggle("is-active",n),i.label?.classList.toggle("is-active",n),n&&(r.add(i.a.node.id),r.add(i.b.node.id))}for(let i of this._particles)i.el.classList.toggle("is-active",r.has(i.node.id));s.classList.add("is-hovering")}render(){return u`
      <svg class="stage" role="img" aria-label="Graphe de relations des entités">
        <defs>
          <marker
            id="sx-graph-arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--line, #334155)"></path>
          </marker>
        </defs>
        <g class="viewport">
          <g class="edges"></g>
          <g class="nodes"></g>
        </g>
      </svg>
      ${this._empty?u`<div class="empty">
            Aucune relation à afficher. Créez des entités et liez-les depuis le
            rail pour voir apparaître le graphe.
          </div>`:u`
            <div class="toolbar">
              <button type="button" title="Zoom avant" aria-label="Zoom avant" @click=${()=>this._zoomBy(1.2)}>+</button>
              <button type="button" title="Zoom arrière" aria-label="Zoom arrière" @click=${()=>this._zoomBy(1/1.2)}>−</button>
              <button type="button" title="Ajuster" aria-label="Ajuster la vue" @click=${()=>this.fit()}>⤢</button>
              <button type="button" title="Réorganiser" aria-label="Réorganiser le graphe" @click=${()=>this.reorganize()}>↻</button>
            </div>
            ${this._legend.length?u`<div class="legend">
                  ${this._legend.map(t=>u`<span><i style=${`background:${t.color}`}></i>${t.label}</span>`)}
                </div>`:null}
          `}
    `}};S.styles=x`
    :host {
      display: block;
      position: relative;
      width: 100%;
      height: var(--graph-height, 560px);
      border: 1px solid var(--line, #cbd5e1);
      border-radius: var(--radius-md, 10px);
      background: var(--surface, #0b1220);
      overflow: hidden;
      contain: strict;
    }
    .stage {
      display: block;
      width: 100%;
      height: 100%;
      cursor: grab;
      touch-action: none;
      user-select: none;
    }
    .stage.is-panning {
      cursor: grabbing;
    }
    .edge {
      stroke: var(--line, #334155);
      stroke-width: 1.4px;
      transition: stroke 0.18s ease, stroke-opacity 0.18s ease;
    }
    .edge-label {
      fill: var(--muted, #94a3b8);
      font-size: 10px;
      paint-order: stroke;
      stroke: var(--surface, #0b1220);
      stroke-width: 3px;
      stroke-linejoin: round;
      pointer-events: none;
      opacity: 0.92;
      transition: opacity 0.18s ease;
    }
    .node {
      cursor: pointer;
    }
    .node circle {
      stroke: var(--surface, #0b1220);
      stroke-width: 2px;
      transition: filter 0.18s ease;
    }
    .node text {
      fill: var(--text, #e2e8f0);
      font-size: 11px;
      font-weight: 600;
      paint-order: stroke;
      stroke: var(--surface, #0b1220);
      stroke-width: 3.5px;
      stroke-linejoin: round;
      pointer-events: none;
    }
    .node:focus-visible {
      outline: none;
    }
    .node:focus-visible circle {
      stroke: var(--accent, #6366f1);
      stroke-width: 3px;
    }
    /* Highlight state driven imperatively. */
    .stage.is-hovering .edge {
      stroke-opacity: 0.15;
    }
    .stage.is-hovering .node {
      opacity: 0.25;
    }
    .stage.is-hovering .edge.is-active {
      stroke-opacity: 1;
      stroke: var(--accent, #6366f1);
    }
    .stage.is-hovering .edge-label {
      opacity: 0.1;
    }
    .stage.is-hovering .edge-label.is-active {
      opacity: 1;
    }
    .stage.is-hovering .node.is-active {
      opacity: 1;
    }
    .node circle:hover {
      filter: brightness(1.15);
    }
    .toolbar {
      position: absolute;
      top: 10px;
      right: 10px;
      display: inline-flex;
      gap: 4px;
      padding: 4px;
      border: 1px solid var(--line, #334155);
      border-radius: 8px;
      background: color-mix(in srgb, var(--surface, #0b1220) 86%, transparent);
      backdrop-filter: blur(4px);
    }
    .toolbar button {
      display: inline-grid;
      place-items: center;
      width: 28px;
      height: 28px;
      padding: 0;
      border: 0;
      border-radius: 6px;
      background: transparent;
      color: var(--muted, #94a3b8);
      font: inherit;
      font-size: 15px;
      line-height: 1;
      cursor: pointer;
    }
    .toolbar button:hover {
      background: color-mix(in srgb, var(--accent, #6366f1) 18%, transparent);
      color: var(--text, #e2e8f0);
    }
    .toolbar button:focus-visible {
      outline: 2px solid var(--accent, #6366f1);
      outline-offset: 1px;
    }
    .legend {
      position: absolute;
      left: 10px;
      bottom: 10px;
      display: flex;
      flex-wrap: wrap;
      gap: 4px 12px;
      max-width: calc(100% - 20px);
      padding: 6px 10px;
      border: 1px solid var(--line, #334155);
      border-radius: 8px;
      background: color-mix(in srgb, var(--surface, #0b1220) 86%, transparent);
      backdrop-filter: blur(4px);
      font-size: 11px;
      color: var(--muted, #94a3b8);
    }
    .legend span {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .legend i {
      width: 9px;
      height: 9px;
      border-radius: 50%;
    }
    .empty {
      position: absolute;
      inset: 0;
      display: grid;
      place-items: center;
      padding: 24px;
      text-align: center;
      color: var(--muted, #94a3b8);
      font-size: 13px;
    }
    .hint {
      position: absolute;
      bottom: 10px;
      right: 10px;
      color: var(--muted, #94a3b8);
      font-size: 10px;
      opacity: 0.7;
      pointer-events: none;
    }
  `,c([v({attribute:!1})],S.prototype,"data",2),c([v({attribute:"storage-key"})],S.prototype,"storageKey",2),c([at()],S.prototype,"_empty",2),S=c([g("sx-entity-graph")],S);var Q=class extends f{render(){return u`
      <div class="section identity" part="identity">
        <slot name="identity"></slot>
      </div>
      <div class="section" part="properties">
        <slot name="properties"></slot>
      </div>
      <div class="section" part="relations">
        <slot name="relations"></slot>
      </div>
      <div class="section" part="sources">
        <slot name="sources"></slot>
      </div>
    `}};Q.styles=x`
    :host {
      display: none;
    }
    :host(:not([hidden])) {
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .section {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .section:not(.identity) {
      padding-top: 14px;
      border-top: 1px solid var(--line, #cbd5e1);
    }
  `,Q=c([g("sx-entity-panel")],Q);var tt=class extends f{render(){return u`<div class="property" part="property">
      <span class="label" part="label"><slot name="label"></slot></span>
      <span class="value" part="value"><slot></slot></span>
      <span class="actions" part="actions"><slot name="actions"></slot></span>
    </div>`}};tt.styles=x`
    :host {
      display: block;
    }
    .property {
      display: grid;
      grid-template-columns: minmax(100px, auto) minmax(0, 1fr) auto;
      gap: 8px;
      align-items: center;
      font-size: 13px;
    }
    .label {
      color: var(--secondary, #06b6d4);
      text-transform: capitalize;
      overflow-wrap: anywhere;
    }
    .value {
      color: var(--text, #0f172a);
      overflow-wrap: anywhere;
    }
    .actions {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    @media (max-width: 540px) {
      .property {
        grid-template-columns: 1fr auto;
      }
      .label {
        grid-column: 1 / -1;
      }
    }
  `,tt=c([g("sx-property")],tt);var de={tiktok:{color:"#EE1D52",path:"M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"},instagram:{color:"#E4405F",path:"M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077"},x:{color:"currentColor",path:"M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z"},facebook:{color:"#1877F2",path:"M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z"},youtube:{color:"#FF0000",path:"M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"},googlemaps:{color:"#1A73E8",path:"M19.527 4.799c1.212 2.608.937 5.678-.405 8.173-1.101 2.047-2.744 3.74-4.098 5.614-.619.858-1.244 1.75-1.669 2.727-.141.325-.263.658-.383.992-.121.333-.224.673-.34 1.008-.109.314-.236.684-.627.687h-.007c-.466-.001-.579-.53-.695-.887-.284-.874-.581-1.713-1.019-2.525-.51-.944-1.145-1.817-1.79-2.671L19.527 4.799zM8.545 7.705l-3.959 4.707c.724 1.54 1.821 2.863 2.871 4.18.247.31.494.622.737.936l4.984-5.925-.029.01c-1.741.601-3.691-.291-4.392-1.987a3.377 3.377 0 0 1-.209-.716c-.063-.437-.077-.761-.004-1.198l.001-.007zM5.492 3.149l-.003.004c-1.947 2.466-2.281 5.88-1.117 8.77l4.785-5.689-.058-.05-3.607-3.035zM14.661.436l-3.838 4.563a.295.295 0 0 1 .027-.01c1.6-.551 3.403.15 4.22 1.626.176.319.323.683.377 1.045.068.446.085.773.012 1.22l-.003.016 3.836-4.561A8.382 8.382 0 0 0 14.67.439l-.009-.003zM9.466 5.868L14.162.285l-.047-.012A8.31 8.31 0 0 0 11.986 0a8.439 8.439 0 0 0-6.169 2.766l-.016.018 3.665 3.084z"},telegram:{color:"#229ED9",path:"M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"},snapchat:{color:"#E0A800",path:"M12.206.793c.99 0 4.347.276 5.93 3.821.529 1.193.403 3.219.299 4.847l-.003.06c-.012.18-.022.345-.03.51.075.045.203.09.401.09.3-.016.659-.12 1.033-.301.165-.088.344-.104.464-.104.182 0 .359.029.509.09.45.149.734.479.734.838.015.449-.39.839-1.213 1.168-.089.029-.209.075-.344.119-.45.135-1.139.36-1.333.81-.09.224-.061.524.12.868l.015.015c.06.136 1.526 3.475 4.791 4.014.255.044.435.27.42.509 0 .075-.015.149-.045.225-.24.569-1.273.988-3.146 1.271-.059.091-.12.375-.164.57-.029.179-.074.36-.134.553-.076.271-.27.405-.555.405h-.03c-.135 0-.313-.031-.538-.074-.36-.075-.765-.135-1.273-.135-.3 0-.599.015-.913.074-.6.104-1.123.464-1.723.884-.853.599-1.826 1.288-3.294 1.288-.06 0-.119-.015-.18-.015h-.149c-1.468 0-2.427-.675-3.279-1.288-.599-.42-1.107-.779-1.707-.884-.314-.045-.629-.074-.928-.074-.54 0-.958.089-1.272.149-.211.043-.391.074-.54.074-.374 0-.523-.224-.583-.42-.061-.192-.09-.389-.135-.567-.046-.181-.105-.494-.166-.57-1.918-.222-2.95-.642-3.189-1.226-.031-.063-.052-.15-.055-.225-.015-.243.165-.465.42-.509 3.264-.54 4.73-3.879 4.791-4.02l.016-.029c.18-.345.224-.645.119-.869-.195-.434-.884-.658-1.332-.809-.121-.029-.24-.074-.346-.119-1.107-.435-1.257-.93-1.197-1.273.09-.479.674-.793 1.168-.793.146 0 .27.029.383.074.42.194.789.3 1.104.3.234 0 .384-.06.465-.105l-.046-.569c-.098-1.626-.225-3.651.307-4.837C7.392 1.077 10.739.807 11.727.807l.419-.015h.06z"},pinterest:{color:"#BD081C",path:"M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.162-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.401.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.354-.629-2.758-1.379l-.749 2.848c-.269 1.045-1.004 2.352-1.498 3.146 1.123.345 2.306.535 3.55.535 6.607 0 11.985-5.365 11.985-11.987C23.97 5.39 18.592.026 11.985.026L12.017 0z"},reddit:{color:"#FF4500",path:"M12 0C5.373 0 0 5.373 0 12c0 3.314 1.343 6.314 3.515 8.485l-2.286 2.286C.775 23.225 1.097 24 1.738 24H12c6.627 0 12-5.373 12-12S18.627 0 12 0Zm4.388 3.199c1.104 0 1.999.895 1.999 1.999 0 1.105-.895 2-1.999 2-.946 0-1.739-.657-1.947-1.539v.002c-1.147.162-2.032 1.15-2.032 2.341v.007c1.776.067 3.4.567 4.686 1.363.473-.363 1.064-.58 1.707-.58 1.547 0 2.802 1.254 2.802 2.802 0 1.117-.655 2.081-1.601 2.531-.088 3.256-3.637 5.876-7.997 5.876-4.361 0-7.905-2.617-7.998-5.87-.954-.447-1.614-1.415-1.614-2.538 0-1.548 1.255-2.802 2.803-2.802.645 0 1.239.218 1.712.585 1.275-.79 2.881-1.291 4.64-1.365v-.01c0-1.663 1.263-3.034 2.88-3.207.188-.911.993-1.595 1.959-1.595Zm-8.085 8.376c-.784 0-1.459.78-1.506 1.797-.047 1.016.64 1.429 1.426 1.429.786 0 1.371-.369 1.418-1.385.047-1.017-.553-1.841-1.338-1.841Zm7.406 0c-.786 0-1.385.824-1.338 1.841.047 1.017.634 1.385 1.418 1.385.785 0 1.473-.413 1.426-1.429-.046-1.017-.721-1.797-1.506-1.797Zm-3.703 4.013c-.974 0-1.907.048-2.77.135-.147.015-.241.168-.183.305.483 1.154 1.622 1.964 2.953 1.964 1.33 0 2.47-.81 2.953-1.964.057-.137-.037-.29-.184-.305-.863-.087-1.795-.135-2.769-.135Z"},whatsapp:{color:"#25D366",path:"M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"}},qt=["#38bdf8","#a78bfa","#34d399","#fbbf24","#f472b6","#22d3ee","#c084fc","#fb7185"],A=class extends f{constructor(){super(...arguments);this.observations=0;this.firstSeen="";this.lastSeen="";this.initial="";this.site="";this.imported=!1;this._menuOpen=!1;this._toggleMenu=t=>{t.stopPropagation(),this._menuOpen?this._closeMenu():this._openMenu()};this._onDocPointerDown=t=>{t.composedPath().includes(this)||this._closeMenu()};this._onKeyDown=t=>{t.key==="Escape"&&this._menuOpen&&(t.stopPropagation(),this._closeMenu())};this._onMenuClick=()=>{this._closeMenu()}}connectedCallback(){super.connectedCallback(),this.addEventListener("keydown",this._onKeyDown)}disconnectedCallback(){super.disconnectedCallback(),this.removeEventListener("keydown",this._onKeyDown),document.removeEventListener("pointerdown",this._onDocPointerDown,!0)}_openMenu(){this._menuOpen=!0,this.toggleAttribute("menu-open",!0),document.addEventListener("pointerdown",this._onDocPointerDown,!0)}_closeMenu(){this._menuOpen&&(this._menuOpen=!1,this.toggleAttribute("menu-open",!1),document.removeEventListener("pointerdown",this._onDocPointerDown,!0))}_brand(){let t=this.site.trim().toLowerCase();if(!t)return null;let r={"t.me":"telegram","telegram.org":"telegram","wa.me":"whatsapp","youtu.be":"youtube","fb.com":"facebook","x.com":"x","twitter.com":"x"}[t];if(!r){let i=t.split(".").filter(Boolean),n=i.length>=2?i[i.length-2]:i[0]??"";r={twitter:"x",google:"googlemaps"}[n]??n}return de[r]??null}get _faviconColor(){let t=(this.site||this.initial||"").toLowerCase();if(!t)return"var(--accent, #6366f1)";let s=0;for(let r=0;r<t.length;r+=1)s=s*31+t.charCodeAt(r)|0;return qt[Math.abs(s)%qt.length]}_fmt(t,s){if(!t)return"";let r=new Date(t.replace(/(\.\d{3})\d+/,"$1"));return Number.isNaN(r.getTime())?"":new Intl.DateTimeFormat(void 0,s).format(r)}_renderFavicon(){let t=this.imported?"Document import\xE9":this.site,s=u`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
      stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 3v4a1 1 0 0 0 1 1h4"></path>
      <path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2Z"></path>
    </svg>`;if(this.imported){let l=this._faviconColor,a=`background: color-mix(in srgb, ${l} 18%, transparent); color: ${l};`;return u`<span class="favicon" style=${a} title=${t} aria-hidden="true">${s}</span>`}let r=this._brand();if(r){let l=r.color==="currentColor",a=l?"var(--text, #e2e8f0)":r.color,h=`background: color-mix(in srgb, ${l?"var(--muted, #94a3b8)":r.color} 18%, transparent); color: ${a};`;return u`<span class="favicon" style=${h} title=${t} aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d=${r.path}></path></svg>
      </span>`}let i=this._faviconColor,n=`background: color-mix(in srgb, ${i} 18%, transparent); color: ${i};`;return u`<span class="favicon" style=${n} title=${t} aria-hidden="true">${this.initial||"\xB7"}</span>`}_renderSeenPill(){let t={day:"numeric",month:"short"},s={dateStyle:"medium",timeStyle:"short"},r=this._fmt(this.firstSeen,t),i=this._fmt(this.lastSeen,t);if(!r&&!i)return null;let n=r&&i&&r!==i?`${r} \u2192 ${i}`:i||r,l=this._fmt(this.firstSeen,s),a=this._fmt(this.lastSeen,s),p=[l?`Premi\xE8re observation : ${l}`:"",a?`Derni\xE8re observation : ${a}`:""].filter(Boolean).join(" \xB7 ");return u`<span class="pill" title=${p} aria-label=${p}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="9"></circle>
        <path d="M12 7v5l3 2"></path>
      </svg>
      ${n}
    </span>`}render(){let t=Number(this.observations)||0,s=`${t} observation${t===1?"":"s"}`;return u`
      <article class="card" part="card">
        <div class="head">
          ${this._renderFavicon()}
          <slot name="title"></slot>
          <slot name="star"></slot>
          <div class="menu-wrap">
            <button
              type="button"
              class="kebab"
              title="Actions supplémentaires"
              aria-label="Actions supplémentaires"
              aria-haspopup="menu"
              aria-expanded=${this._menuOpen?"true":"false"}
              @click=${this._toggleMenu}
            >
              <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <circle cx="12" cy="5" r="1.7"></circle>
                <circle cx="12" cy="12" r="1.7"></circle>
                <circle cx="12" cy="19" r="1.7"></circle>
              </svg>
            </button>
            <div class="menu" role="menu" ?hidden=${!this._menuOpen} @click=${this._onMenuClick}>
              <div class="menu__label">Actions supplémentaires</div>
              <slot name="menu"></slot>
            </div>
          </div>
        </div>
        <div class="sub">
          <slot name="status"></slot>
          <span class="pill" title=${s} aria-label=${s}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
            ${t}
          </span>
          ${this._renderSeenPill()}
        </div>
        <slot name="tags"></slot>
        <slot></slot>
      </article>
    `}};A.styles=x`
    :host {
      display: block;
      position: relative;
      min-width: 0;
      border: 1px solid var(--line, #1e293b);
      border-radius: 10px;
      background: var(--surface, #0b1220);
      cursor: pointer;
      transition: border-color 120ms ease;
    }
    :host(:hover),
    :host(.is-inspected) {
      border-color: var(--accent, #6366f1);
    }
    :host(.is-inspected) {
      box-shadow: 0 0 0 1px var(--accent, #6366f1);
    }
    :host([hidden]) {
      display: none;
    }
    /* Raise the whole card above its grid neighbours while the overflow menu is
       open, so the popover is not clipped behind the next card. */
    :host([menu-open]) {
      z-index: 20;
    }
    .card {
      display: grid;
      gap: 7px;
      padding: 11px 12px;
    }
    .head {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }
    .favicon {
      flex: 0 0 auto;
      display: grid;
      place-items: center;
      width: 24px;
      height: 24px;
      border-radius: 7px;
      font: 700 12px/1 var(--font-ui, system-ui, sans-serif);
      text-transform: uppercase;
    }
    .favicon svg {
      width: 15px;
      height: 15px;
    }
    ::slotted([slot="title"]) {
      flex: 0 1 auto;
      min-width: 0;
    }
    ::slotted([slot="star"]) {
      flex: 0 0 auto;
      margin-left: auto;
    }
    .menu-wrap {
      position: relative;
      display: inline-flex;
      flex: 0 0 auto;
    }
    .kebab {
      display: grid;
      place-items: center;
      width: 30px;
      height: 30px;
      padding: 0;
      border: 0;
      border-radius: 7px;
      background: transparent;
      color: var(--muted, #94a3b8);
      cursor: pointer;
      transition: background-color 120ms ease, color 120ms ease;
    }
    .kebab:hover,
    .kebab[aria-expanded="true"] {
      background: color-mix(in srgb, var(--accent, #6366f1) 16%, transparent);
      color: var(--text, #e2e8f0);
    }
    .kebab:focus-visible {
      outline: 2px solid var(--accent, #6366f1);
      outline-offset: 1px;
    }
    .kebab svg {
      width: 18px;
      height: 18px;
    }
    .menu {
      position: absolute;
      top: calc(100% + 6px);
      right: 0;
      z-index: 30;
      min-width: 212px;
      padding: 5px;
      border: 1px solid var(--line, #334155);
      border-radius: 10px;
      background: var(--surface, #0b1220);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.38);
    }
    .menu[hidden] {
      display: none;
    }
    .menu__label {
      padding: 4px 8px 6px;
      color: var(--muted, #94a3b8);
      font-size: 11px;
    }
    .sub {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }
    ::slotted([slot="status"]) {
      flex: 0 0 auto;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      flex: 0 0 auto;
      color: var(--muted, #94a3b8);
      font-size: 11px;
      font-variant-numeric: tabular-nums;
    }
    .pill svg {
      width: 13px;
      height: 13px;
      opacity: 0.85;
    }
    ::slotted([slot="tags"]) {
      min-width: 0;
    }
  `,c([v({type:Number})],A.prototype,"observations",2),c([v({attribute:"first-seen"})],A.prototype,"firstSeen",2),c([v({attribute:"last-seen"})],A.prototype,"lastSeen",2),c([v()],A.prototype,"initial",2),c([v()],A.prototype,"site",2),c([v({type:Boolean})],A.prototype,"imported",2),c([at()],A.prototype,"_menuOpen",2),A=c([g("sx-saved-page-card")],A);var et=class extends f{render(){return u`
      <article class="card" part="card">
        <div class="head">
          <span class="icon-avatar" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="4" width="18" height="4" rx="1"></rect>
              <path d="M5 8v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8"></path>
              <path d="M10 12h4"></path>
            </svg>
          </span>
          <div class="title-block">
            <slot name="title"></slot>
            <slot name="timestamp"></slot>
          </div>
        </div>
        <div class="stats">
          <slot name="stat"></slot>
        </div>
        <slot name="description"></slot>
        <div class="links">
          <slot name="link"></slot>
          <slot name="delete"></slot>
        </div>
      </article>
    `}};et.styles=x`
    :host {
      display: block;
      border: 1px solid var(--line, #1e293b);
      border-radius: 10px;
      background: var(--surface, #0b1220);
      transition: border-color 120ms ease;
    }
    :host(:hover) {
      border-color: var(--accent, #6366f1);
    }
    .card {
      display: grid;
      gap: 10px;
      padding: 14px;
    }
    .head {
      display: flex;
      align-items: flex-start;
      gap: 10px;
    }
    .icon-avatar {
      flex: 0 0 auto;
      display: grid;
      place-items: center;
      width: 30px;
      height: 30px;
      border-radius: 8px;
      background: color-mix(in srgb, var(--accent, #6366f1) 18%, transparent);
      color: var(--accent, #6366f1);
    }
    .icon-avatar svg {
      width: 17px;
      height: 17px;
    }
    .title-block {
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      gap: 4px 10px;
      min-width: 0;
    }
    ::slotted([slot="title"]) {
      color: var(--text, #e2e8f0);
      font-size: 14px;
    }
    ::slotted([slot="timestamp"]) {
      color: var(--muted, #94a3b8);
      font-size: 12px;
    }
    .stats {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    ::slotted([slot="stat"]) {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 0 8px;
      border: 1px solid var(--line, #334155);
      border-radius: 6px;
      background: var(--surface-2, #172033);
      color: var(--muted, #94a3b8);
      font-size: 11px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }
    ::slotted([slot="description"]) {
      color: var(--muted, #94a3b8);
      font-size: 12px;
      font-style: italic;
    }
    .links {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 6px;
    }
    ::slotted([slot="link"]) {
      display: inline-flex !important;
      align-items: center;
      gap: 5px;
      height: 26px;
      padding: 0 10px;
      border: 1px solid var(--line, #334155);
      border-radius: 999px;
      background: var(--surface-2, #172033);
      color: var(--accent, #6366f1);
      font-size: 12px;
      font-weight: 600;
      text-decoration: none;
      transition: border-color 120ms ease, background-color 120ms ease;
    }
    ::slotted([slot="link"]:hover) {
      border-color: var(--accent, #6366f1);
      background: color-mix(in srgb, var(--accent, #6366f1) 12%, transparent);
    }
    ::slotted([slot="link"]) svg {
      width: 13px;
      height: 13px;
    }
    ::slotted([slot="delete"]) {
      display: inline-flex !important;
      align-items: center;
      gap: 5px;
      height: 26px;
      padding: 0 10px;
      margin-left: auto;
      border: 1px solid color-mix(in srgb, var(--danger, #f87171) 45%, var(--line, #334155));
      border-radius: 999px;
      background: transparent;
      color: var(--danger, #f87171);
      font: inherit;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      text-decoration: none;
    }
    ::slotted([slot="delete"]:hover) {
      background: color-mix(in srgb, var(--danger, #f87171) 10%, transparent);
    }
    ::slotted([slot="delete"]:disabled) {
      cursor: not-allowed;
      opacity: 0.5;
    }
    ::slotted([slot="delete"]) svg {
      width: 13px;
      height: 13px;
    }
  `,et=c([g("sx-export-card")],et);var ct=class extends f{render(){return u`<slot></slot>`}};ct=c([g("sx-extracted-entity-row")],ct);var dt=class extends f{render(){return u`<slot></slot>`}};dt=c([g("sx-evidence-item")],dt);var pt=class extends f{render(){return u`<slot></slot>`}};pt=c([g("sx-page-monitor-card")],pt);var ht=class extends f{render(){return u`<slot></slot>`}};ht=c([g("sx-url-analysis")],ht);})();
