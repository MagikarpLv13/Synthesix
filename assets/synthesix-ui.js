"use strict";(()=>{var Bt=Object.defineProperty;var Vt=Object.getOwnPropertyDescriptor;var p=(n,e,t,s)=>{for(var i=s>1?void 0:s?Vt(e,t):e,r=n.length-1,o;r>=0;r--)(o=n[r])&&(i=(s?o(e,t,i):o(i))||i);return s&&i&&Bt(e,t,i),i};var et=globalThis,st=et.ShadowRoot&&(et.ShadyCSS===void 0||et.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,lt=Symbol(),xt=new WeakMap,q=class{constructor(e,t,s){if(this._$cssResult$=!0,s!==lt)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(st&&e===void 0){let s=t!==void 0&&t.length===1;s&&(e=xt.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),s&&xt.set(t,e))}return e}toString(){return this.cssText}},$t=n=>new q(typeof n=="string"?n:n+"",void 0,lt),b=(n,...e)=>{let t=n.length===1?n[0]:e.reduce((s,i,r)=>s+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+n[r+1],n[0]);return new q(t,n,lt)},wt=(n,e)=>{if(st)n.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let s=document.createElement("style"),i=et.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=t.cssText,n.appendChild(s)}},ct=st?n=>n:n=>n instanceof CSSStyleSheet?(e=>{let t="";for(let s of e.cssRules)t+=s.cssText;return $t(t)})(n):n;var{is:jt,defineProperty:qt,getOwnPropertyDescriptor:It,getOwnPropertyNames:Ft,getOwnPropertySymbols:Kt,getPrototypeOf:Wt}=Object,it=globalThis,At=it.trustedTypes,Zt=At?At.emptyScript:"",Yt=it.reactiveElementPolyfillSupport,I=(n,e)=>n,F={toAttribute(n,e){switch(e){case Boolean:n=n?Zt:null;break;case Object:case Array:n=n==null?n:JSON.stringify(n)}return n},fromAttribute(n,e){let t=n;switch(e){case Boolean:t=n!==null;break;case Number:t=n===null?null:Number(n);break;case Object:case Array:try{t=JSON.parse(n)}catch{t=null}}return t}},rt=(n,e)=>!jt(n,e),kt={attribute:!0,type:String,converter:F,reflect:!1,useDefault:!1,hasChanged:rt};Symbol.metadata??=Symbol("metadata"),it.litPropertyMetadata??=new WeakMap;var E=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=kt){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(e,s,t);i!==void 0&&qt(this.prototype,e,i)}}static getPropertyDescriptor(e,t,s){let{get:i,set:r}=It(this.prototype,e)??{get(){return this[t]},set(o){this[t]=o}};return{get:i,set(o){let l=i?.call(this);r?.call(this,o),this.requestUpdate(e,l,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??kt}static _$Ei(){if(this.hasOwnProperty(I("elementProperties")))return;let e=Wt(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(I("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(I("properties"))){let t=this.properties,s=[...Ft(t),...Kt(t)];for(let i of s)this.createProperty(i,t[i])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[s,i]of t)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[t,s]of this.elementProperties){let i=this._$Eu(t,s);i!==void 0&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let s=new Set(e.flat(1/0).reverse());for(let i of s)t.unshift(ct(i))}else e!==void 0&&t.push(ct(e));return t}static _$Eu(e,t){let s=t.attribute;return s===!1?void 0:typeof s=="string"?s:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let s of t.keys())this.hasOwnProperty(s)&&(e.set(s,this[s]),delete this[s]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return wt(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,s){this._$AK(e,s)}_$ET(e,t){let s=this.constructor.elementProperties.get(e),i=this.constructor._$Eu(e,s);if(i!==void 0&&s.reflect===!0){let r=(s.converter?.toAttribute!==void 0?s.converter:F).toAttribute(t,s.type);this._$Em=e,r==null?this.removeAttribute(i):this.setAttribute(i,r),this._$Em=null}}_$AK(e,t){let s=this.constructor,i=s._$Eh.get(e);if(i!==void 0&&this._$Em!==i){let r=s.getPropertyOptions(i),o=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:F;this._$Em=i;let l=o.fromAttribute(t,r.type);this[i]=l??this._$Ej?.get(i)??l,this._$Em=null}}requestUpdate(e,t,s,i=!1,r){if(e!==void 0){let o=this.constructor;if(i===!1&&(r=this[e]),s??=o.getPropertyOptions(e),!((s.hasChanged??rt)(r,t)||s.useDefault&&s.reflect&&r===this._$Ej?.get(e)&&!this.hasAttribute(o._$Eu(e,s))))return;this.C(e,t,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:s,reflect:i,wrapped:r},o){s&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,o??t??this[e]),r!==!0||o!==void 0)||(this._$AL.has(e)||(this.hasUpdated||s||(t=void 0),this._$AL.set(e,t)),i===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,r]of this._$Ep)this[i]=r;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,r]of s){let{wrapped:o}=r,l=this[i];o!==!0||this._$AL.has(i)||l===void 0||this.C(i,void 0,r,l)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(t)):this._$EM()}catch(s){throw e=!1,this._$EM(),s}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};E.elementStyles=[],E.shadowRootOptions={mode:"open"},E[I("elementProperties")]=new Map,E[I("finalized")]=new Map,Yt?.({ReactiveElement:E}),(it.reactiveElementVersions??=[]).push("2.1.2");var gt=globalThis,Et=n=>n,ot=gt.trustedTypes,Mt=ot?ot.createPolicy("lit-html",{createHTML:n=>n}):void 0,Tt="$lit$",M=`lit$${Math.random().toFixed(9).slice(2)}$`,Nt="?"+M,Xt=`<${Nt}>`,N=document,W=()=>N.createComment(""),Z=n=>n===null||typeof n!="object"&&typeof n!="function",vt=Array.isArray,Jt=n=>vt(n)||typeof n?.[Symbol.iterator]=="function",dt=`[ 	
\f\r]`,K=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Ct=/-->/g,Lt=/>/g,P=RegExp(`>|${dt}(?:([^\\s"'>=/]+)(${dt}*=${dt}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),St=/'/g,Ot=/"/g,zt=/^(?:script|style|textarea|title)$/i,bt=n=>(e,...t)=>({_$litType$:n,strings:e,values:t}),m=bt(1),pe=bt(2),he=bt(3),z=Symbol.for("lit-noChange"),$=Symbol.for("lit-nothing"),Pt=new WeakMap,T=N.createTreeWalker(N,129);function Ht(n,e){if(!vt(n)||!n.hasOwnProperty("raw"))throw Error("invalid template strings array");return Mt!==void 0?Mt.createHTML(e):e}var Qt=(n,e)=>{let t=n.length-1,s=[],i,r=e===2?"<svg>":e===3?"<math>":"",o=K;for(let l=0;l<t;l++){let a=n[l],d,h,u=-1,v=0;for(;v<a.length&&(o.lastIndex=v,h=o.exec(a),h!==null);)v=o.lastIndex,o===K?h[1]==="!--"?o=Ct:h[1]!==void 0?o=Lt:h[2]!==void 0?(zt.test(h[2])&&(i=RegExp("</"+h[2],"g")),o=P):h[3]!==void 0&&(o=P):o===P?h[0]===">"?(o=i??K,u=-1):h[1]===void 0?u=-2:(u=o.lastIndex-h[2].length,d=h[1],o=h[3]===void 0?P:h[3]==='"'?Ot:St):o===Ot||o===St?o=P:o===Ct||o===Lt?o=K:(o=P,i=void 0);let c=o===P&&n[l+1].startsWith("/>")?" ":"";r+=o===K?a+Xt:u>=0?(s.push(d),a.slice(0,u)+Tt+a.slice(u)+M+c):a+M+(u===-2?l:c)}return[Ht(n,r+(n[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),s]},Y=class n{constructor({strings:e,_$litType$:t},s){let i;this.parts=[];let r=0,o=0,l=e.length-1,a=this.parts,[d,h]=Qt(e,t);if(this.el=n.createElement(d,s),T.currentNode=this.el.content,t===2||t===3){let u=this.el.content.firstChild;u.replaceWith(...u.childNodes)}for(;(i=T.nextNode())!==null&&a.length<l;){if(i.nodeType===1){if(i.hasAttributes())for(let u of i.getAttributeNames())if(u.endsWith(Tt)){let v=h[o++],c=i.getAttribute(u).split(M),_=/([.?@])?(.*)/.exec(v);a.push({type:1,index:r,name:_[2],strings:c,ctor:_[1]==="."?ht:_[1]==="?"?ut:_[1]==="@"?mt:U}),i.removeAttribute(u)}else u.startsWith(M)&&(a.push({type:6,index:r}),i.removeAttribute(u));if(zt.test(i.tagName)){let u=i.textContent.split(M),v=u.length-1;if(v>0){i.textContent=ot?ot.emptyScript:"";for(let c=0;c<v;c++)i.append(u[c],W()),T.nextNode(),a.push({type:2,index:++r});i.append(u[v],W())}}}else if(i.nodeType===8)if(i.data===Nt)a.push({type:2,index:r});else{let u=-1;for(;(u=i.data.indexOf(M,u+1))!==-1;)a.push({type:7,index:r}),u+=M.length-1}r++}}static createElement(e,t){let s=N.createElement("template");return s.innerHTML=e,s}};function D(n,e,t=n,s){if(e===z)return e;let i=s!==void 0?t._$Co?.[s]:t._$Cl,r=Z(e)?void 0:e._$litDirective$;return i?.constructor!==r&&(i?._$AO?.(!1),r===void 0?i=void 0:(i=new r(n),i._$AT(n,t,s)),s!==void 0?(t._$Co??=[])[s]=i:t._$Cl=i),i!==void 0&&(e=D(n,i._$AS(n,e.values),i,s)),e}var pt=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:s}=this._$AD,i=(e?.creationScope??N).importNode(t,!0);T.currentNode=i;let r=T.nextNode(),o=0,l=0,a=s[0];for(;a!==void 0;){if(o===a.index){let d;a.type===2?d=new X(r,r.nextSibling,this,e):a.type===1?d=new a.ctor(r,a.name,a.strings,this,e):a.type===6&&(d=new ft(r,this,e)),this._$AV.push(d),a=s[++l]}o!==a?.index&&(r=T.nextNode(),o++)}return T.currentNode=N,i}p(e){let t=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(e,s,t),t+=s.strings.length-2):s._$AI(e[t])),t++}},X=class n{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,s,i){this.type=2,this._$AH=$,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=D(this,e,t),Z(e)?e===$||e==null||e===""?(this._$AH!==$&&this._$AR(),this._$AH=$):e!==this._$AH&&e!==z&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Jt(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==$&&Z(this._$AH)?this._$AA.nextSibling.data=e:this.T(N.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:s}=e,i=typeof s=="number"?this._$AC(e):(s.el===void 0&&(s.el=Y.createElement(Ht(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(t);else{let r=new pt(i,this),o=r.u(this.options);r.p(t),this.T(o),this._$AH=r}}_$AC(e){let t=Pt.get(e.strings);return t===void 0&&Pt.set(e.strings,t=new Y(e)),t}k(e){vt(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,s,i=0;for(let r of e)i===t.length?t.push(s=new n(this.O(W()),this.O(W()),this,this.options)):s=t[i],s._$AI(r),i++;i<t.length&&(this._$AR(s&&s._$AB.nextSibling,i),t.length=i)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let s=Et(e).nextSibling;Et(e).remove(),e=s}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},U=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,s,i,r){this.type=1,this._$AH=$,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=r,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=$}_$AI(e,t=this,s,i){let r=this.strings,o=!1;if(r===void 0)e=D(this,e,t,0),o=!Z(e)||e!==this._$AH&&e!==z,o&&(this._$AH=e);else{let l=e,a,d;for(e=r[0],a=0;a<r.length-1;a++)d=D(this,l[s+a],t,a),d===z&&(d=this._$AH[a]),o||=!Z(d)||d!==this._$AH[a],d===$?e=$:e!==$&&(e+=(d??"")+r[a+1]),this._$AH[a]=d}o&&!i&&this.j(e)}j(e){e===$?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},ht=class extends U{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===$?void 0:e}},ut=class extends U{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==$)}},mt=class extends U{constructor(e,t,s,i,r){super(e,t,s,i,r),this.type=5}_$AI(e,t=this){if((e=D(this,e,t,0)??$)===z)return;let s=this._$AH,i=e===$&&s!==$||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,r=e!==$&&(s===$||i);i&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},ft=class{constructor(e,t,s){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(e){D(this,e)}};var te=gt.litHtmlPolyfillSupport;te?.(Y,X),(gt.litHtmlVersions??=[]).push("3.3.3");var Rt=(n,e,t)=>{let s=t?.renderBefore??e,i=s._$litPart$;if(i===void 0){let r=t?.renderBefore??null;s._$litPart$=i=new X(e.insertBefore(W(),r),r,void 0,t??{})}return i._$AI(n),i};var yt=globalThis,g=class extends E{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Rt(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return z}};g._$litElement$=!0,g.finalized=!0,yt.litElementHydrateSupport?.({LitElement:g});var ee=yt.litElementPolyfillSupport;ee?.({LitElement:g});(yt.litElementVersions??=[]).push("4.2.2");var y=n=>(e,t)=>{t!==void 0?t.addInitializer(()=>{customElements.define(n,e)}):customElements.define(n,e)};var se={attribute:!0,type:String,converter:F,reflect:!1,hasChanged:rt},ie=(n=se,e,t)=>{let{kind:s,metadata:i}=t,r=globalThis.litPropertyMetadata.get(i);if(r===void 0&&globalThis.litPropertyMetadata.set(i,r=new Map),s==="setter"&&((n=Object.create(n)).wrapped=!0),r.set(t.name,n),s==="accessor"){let{name:o}=t;return{set(l){let a=e.get.call(this);e.set.call(this,l),this.requestUpdate(o,a,n,!0,l)},init(l){return l!==void 0&&this.C(o,void 0,n,l),l}}}if(s==="setter"){let{name:o}=t;return function(l){let a=this[o];e.call(this,l),this.requestUpdate(o,a,n,!0,l)}}throw Error("Unsupported decorator location: "+s)};function f(n){return(e,t)=>typeof t=="object"?ie(n,e,t):((s,i,r)=>{let o=i.hasOwnProperty(r);return i.constructor.createProperty(r,s),o?Object.getOwnPropertyDescriptor(i,r):void 0})(n,e,t)}function nt(n){return f({...n,state:!0,attribute:!1})}var G=class extends g{constructor(){super(...arguments);this.tone="neutral"}render(){return m`<span class="chip"><slot></slot></span>`}};G.styles=b`
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
  `,p([f({reflect:!0})],G.prototype,"tone",2),G=p([y("sx-chip")],G);var H=class extends g{constructor(){super(...arguments);this.accent="none";this.triage=!1}willUpdate(t){t.has("triage")&&(this.triage?(this.setAttribute("data-triage-item",""),this.hasAttribute("tabindex")||this.setAttribute("tabindex","0")):this.removeAttribute("data-triage-item"))}render(){return m`
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
    `}};H.styles=b`
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
  `,p([f({reflect:!0})],H.prototype,"accent",2),p([f({type:Boolean,reflect:!0})],H.prototype,"triage",2),H=p([y("sx-result-card")],H);var R=class extends g{constructor(){super(...arguments);this.level="none";this.expandable=!1}render(){let t=m`<span class="value" part="value"><slot></slot></span>`;return this.expandable?m`
      <details class="score" part="score">
        <summary part="summary">${t}</summary>
        <ul class="list" part="breakdown">
          <slot name="breakdown"></slot>
        </ul>
        <small class="note" part="note">
          <slot name="note"></slot>
        </small>
      </details>
    `:m`<span class="score" part="score">${t}</span>`}};R.styles=b`
    :host {
      display: inline-block;
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

    details.score {
      display: inline-block;
    }

    summary {
      list-style: none;
      cursor: pointer;
    }

    summary::-webkit-details-marker {
      display: none;
    }

    summary:focus-visible .value {
      outline: none;
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }

    .list {
      margin: 8px 0 4px;
      padding-left: 18px;
      font-size: 12px;
      color: var(--muted, #64748b);
    }

    .note {
      display: block;
      font-size: 11px;
      color: var(--muted, #64748b);
    }

    ::slotted([slot="note"]) {
      color: var(--muted, #64748b);
    }
  `,p([f({reflect:!0})],R.prototype,"level",2),p([f({type:Boolean,reflect:!0})],R.prototype,"expandable",2),R=p([y("sx-score")],R);var C=class extends g{constructor(){super(...arguments);this.tone="muted";this.removable=!1;this.removeLabel="Remove"}_remove(){this.dispatchEvent(new CustomEvent("sx-tag-remove",{bubbles:!0,composed:!0}))}render(){return m`<span class="tag" part="tag">
      <slot></slot>
      ${this.removable?m`<button
            class="remove"
            part="remove"
            type="button"
            aria-label=${this.removeLabel}
            @click=${this._remove}
          >
            &times;
          </button>`:null}
    </span>`}};C.styles=b`
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
  `,p([f({reflect:!0})],C.prototype,"tone",2),p([f({type:Boolean,reflect:!0})],C.prototype,"removable",2),p([f({attribute:"remove-label"})],C.prototype,"removeLabel",2),C=p([y("sx-tag")],C);var J=class extends g{render(){return m`<span class="provenance" part="provenance">
      <slot name="icon"></slot>
      <span class="label" part="label"><slot name="label"></slot></span>
      <span class="detail" part="detail"><slot></slot></span>
    </span>`}};J.styles=b`
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
  `,J=p([y("sx-provenance")],J);var B=class extends g{constructor(){super(...arguments);this.status="pending"}render(){return m`<span
      class="badge"
      part="badge"
      role="status"
      aria-live="polite"
    >
      <slot></slot>
    </span>`}};B.styles=b`
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
  `,p([f({reflect:!0})],B.prototype,"status",2),B=p([y("sx-evidence-badge")],B);var L=class extends g{constructor(){super(...arguments);this.selected="";this.pane="list";this.backLabel="Back to list"}get _items(){return Array.from(this.querySelectorAll("[data-inspector-item]"))}get _panels(){return Array.from(this.querySelectorAll("[data-inspector-panel]"))}_valueOf(t){return t.getAttribute("data-inspector-item")??""}firstUpdated(){if(!this.selected){let t=this._items[0];t&&(this.selected=this._valueOf(t))}this._sync()}updated(t){t.has("selected")&&this._sync()}_sync(){let t=this.selected;for(let s of this._items)this._valueOf(s)===t?s.setAttribute("aria-current","true"):s.removeAttribute("aria-current");for(let s of this._panels)s.hidden=s.getAttribute("data-inspector-panel")!==t}_select(t,s=!1){if(t===this.selected){this.pane="detail";return}let i=this.selected;this.selected=t,this.pane="detail",this.dispatchEvent(new CustomEvent("sx-inspector-select",{detail:{value:t,previous:i},bubbles:!0,composed:!0})),s&&this.updateComplete.then(()=>{this._items.find(o=>this._valueOf(o)===t)?.focus()})}_onListClick(t){let i=t.target?.closest("[data-inspector-item]");i&&this.contains(i)&&this._select(this._valueOf(i))}_onListKeydown(t){if(!["ArrowDown","ArrowUp","Home","End"].includes(t.key))return;let i=this._items;if(!i.length)return;let r=i.findIndex(l=>this._valueOf(l)===this.selected),o=r;t.key==="ArrowDown"?o=Math.min(i.length-1,r+1):t.key==="ArrowUp"?o=Math.max(0,r-1):t.key==="Home"?o=0:t.key==="End"&&(o=i.length-1),o!==r&&(t.preventDefault(),this._select(this._valueOf(i[o]),!0))}_onBack(){this.pane="list",this.updateComplete.then(()=>{this._items.find(s=>this._valueOf(s)===this.selected)?.focus()})}_onSlotChange(){if(!this.selected){let t=this._items[0];if(t){this.selected=t.getAttribute("data-inspector-item")??"";return}}this._sync()}render(){return m`
      <div class="frame" part="frame">
        <div class="list" part="list">
          <div class="header" part="list-header"><slot name="list-header"></slot></div>
          <div
            class="list-body"
            @click=${this._onListClick}
            @keydown=${this._onListKeydown}
          >
            <slot name="list" @slotchange=${this._onSlotChange}></slot>
          </div>
        </div>
        <div class="detail" part="detail">
          <div class="detail-header" part="detail-header">
            <button
              class="back"
              part="back"
              type="button"
              aria-label=${this.backLabel}
              @click=${this._onBack}
            >
              ‹ <slot name="back-label">Back</slot>
            </button>
            <div class="header"><slot name="detail-header"></slot></div>
          </div>
          <div class="detail-body" part="detail-body">
            <slot name="detail" @slotchange=${this._onSlotChange}></slot>
          </div>
        </div>
      </div>
    `}};L.styles=b`
    :host {
      display: block;
    }
    .frame {
      display: grid;
      grid-template-columns: minmax(220px, 320px) 1fr;
      gap: var(--space-4, 16px);
      align-items: start;
    }
    .list {
      display: flex;
      flex-direction: column;
      gap: var(--space-2, 8px);
      min-width: 0;
    }
    .list-body {
      display: flex;
      flex-direction: column;
      gap: 6px;
      min-width: 0;
      max-height: var(--sx-inspector-list-h, 70vh);
      overflow: auto;
    }
    .detail {
      min-width: 0;
    }
    .detail-header {
      display: flex;
      align-items: center;
      gap: var(--space-2, 8px);
      margin-bottom: var(--space-2, 8px);
    }
    .detail-header:empty {
      display: none;
    }
    .header {
      font-size: 13px;
      font-weight: 600;
      color: var(--muted, #64748b);
    }
    .back {
      display: none;
      align-items: center;
      gap: 4px;
      font: inherit;
      font-size: 13px;
      padding: 4px 8px;
      border: 1px solid var(--line, #cbd5e1);
      border-radius: var(--radius-sm, 6px);
      background: var(--surface, #ffffff);
      color: var(--text, #0f172a);
      cursor: pointer;
    }
    .back:hover {
      border-color: var(--accent, #2563eb);
    }
    .back:focus-visible {
      outline: none;
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }
    ::slotted([data-inspector-item]) {
      cursor: pointer;
    }
    @media (max-width: 720px) {
      .frame {
        grid-template-columns: 1fr;
      }
      :host([pane="list"]) .detail {
        display: none;
      }
      :host([pane="detail"]) .list {
        display: none;
      }
      .back {
        display: inline-flex;
      }
    }
  `,p([f({reflect:!0})],L.prototype,"selected",2),p([f({reflect:!0})],L.prototype,"pane",2),p([f({attribute:"back-label"})],L.prototype,"backLabel",2),L=p([y("sx-inspector")],L);var S=class extends g{constructor(){super(...arguments);this.kind="";this.confidence="";this.status="candidate"}_onOptionalSlot(t){let s=t.target,i=s.parentElement;if(!i)return;let r=s.assignedNodes({flatten:!0}).some(o=>o.nodeType===Node.ELEMENT_NODE||(o.textContent??"").trim().length>0);i.hidden=!r}render(){return m`
      <article class="entity" part="entity">
        <div class="head" part="head">
          <span class="kind" part="kind">${this.kind}</span>
          ${this.confidence?m`<span class="confidence" part="confidence">${this.confidence}</span>`:null}
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
    `}};S.styles=b`
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
  `,p([f()],S.prototype,"kind",2),p([f()],S.prototype,"confidence",2),p([f({reflect:!0})],S.prototype,"status",2),S=p([y("sx-entity")],S);var Q="http://www.w3.org/2000/svg",Dt={personne:"#38bdf8",entreprise:"#a78bfa",organisation:"#a78bfa",lieu:"#34d399",adresse:"#34d399",\u00E9v\u00E9nement:"#fbbf24",evenement:"#fbbf24",document:"#f472b6",identifiant:"#f59e0b"},Ut=["#38bdf8","#a78bfa","#34d399","#fbbf24","#f472b6","#22d3ee","#c084fc"];function re(n){let e=(n??"").trim().toLowerCase();if(e&&Dt[e])return Dt[e];if(!e)return"#94a3b8";let t=0;for(let s=0;s<e.length;s+=1)t=t*31+e.charCodeAt(s)|0;return Ut[Math.abs(t)%Ut.length]}var O=class extends g{constructor(){super(...arguments);this.data=null;this.storageKey="";this._empty=!1;this._particles=[];this._links=[];this._byId=new Map;this._legend=[];this._k=1;this._tx=0;this._ty=0;this._width=0;this._height=0;this._resizeObs=null;this._laidOut=!1;this._mode="idle";this._dragParticle=null;this._startX=0;this._startY=0;this._moved=!1;this._activeId=null;this._onWheel=t=>{t.preventDefault();let s=this.getBoundingClientRect(),i=t.deltaY<0?1.12:1/1.12;this._zoomBy(i,t.clientX-s.left,t.clientY-s.top)};this._onPointerDown=t=>{if(t.button!==0)return;let i=t.target.closest(".node");if(this._startX=t.clientX,this._startY=t.clientY,this._moved=!1,this._svg?.setPointerCapture(t.pointerId),i?.dataset.id){let r=this._byId.get(i.dataset.id);r&&(this._mode="node",this._dragParticle=r,r.fixed=!0)}else this._mode="pan",this._svg?.classList.add("is-panning");window.addEventListener("pointermove",this._onPointerMove),window.addEventListener("pointerup",this._onPointerUp)};this._onPointerMove=t=>{let s=t.clientX-this._startX,i=t.clientY-this._startY;if(!this._moved&&Math.hypot(s,i)>4&&(this._moved=!0),this._mode==="pan")this._tx+=t.movementX,this._ty+=t.movementY,this._draw();else if(this._mode==="node"&&this._dragParticle){let r=this._toWorld(t.clientX,t.clientY);this._dragParticle.x=r.x,this._dragParticle.y=r.y,this._draw()}};this._onPointerUp=t=>{if(window.removeEventListener("pointermove",this._onPointerMove),window.removeEventListener("pointerup",this._onPointerUp),this._svg?.classList.remove("is-panning"),this._mode==="node"&&this._dragParticle){let s=this._dragParticle;s.fixed=!1,this._moved?this._saveLayout():this._select(s.node.id)}this._mode="idle",this._dragParticle=null}}get _svg(){return this.renderRoot.querySelector(".stage")}get _viewport(){return this.renderRoot.querySelector(".viewport")}get _edgesG(){return this.renderRoot.querySelector(".edges")}get _nodesG(){return this.renderRoot.querySelector(".nodes")}connectedCallback(){super.connectedCallback(),this.data||(this.data=this._readInlineData())}disconnectedCallback(){super.disconnectedCallback(),this._resizeObs?.disconnect(),this._resizeObs=null}firstUpdated(){let t=this._svg;t&&(t.addEventListener("wheel",this._onWheel,{passive:!1}),t.addEventListener("pointerdown",this._onPointerDown)),this._resizeObs=new ResizeObserver(s=>{let i=s[0]?.contentRect;i&&(this._width=i.width,this._height=i.height,!this._laidOut&&this._width>0&&this._height>0&&this._build())}),this._resizeObs.observe(this)}updated(t){t.has("data")&&(this._laidOut=!1,this._width>0&&this._height>0&&this._build())}_readInlineData(){let t=this.querySelector("script[data-graph-data]");if(!t?.textContent)return null;try{let s=JSON.parse(t.textContent);if(Array.isArray(s.nodes))return s}catch{}return null}_build(){let t=this._edgesG,s=this._nodesG;if(!t||!s)return;this.data||(this.data=this._readInlineData()),t.replaceChildren(),s.replaceChildren(),this._particles=[],this._links=[],this._byId.clear();let i=this.data?.nodes??[],r=this.data?.edges??[];if(this._empty=i.length===0,this._empty){this._laidOut=!0;return}let o=new Map,l=[],a=new Set(i.map(c=>c.id));for(let c of r)c.source!==c.target&&(!a.has(c.source)||!a.has(c.target)||(l.push(c),o.set(c.source,(o.get(c.source)??0)+1),o.set(c.target,(o.get(c.target)??0)+1)));let d=this._loadLayout(),h=i.length,u=50*Math.sqrt(h)+60,v=new Map;i.forEach((c,_)=>{let A=o.get(c.id)??0,w=re(c.category);c.category&&v.set(c.category,w);let x=d?.[c.id],V=Math.random()*Math.PI*2,_t=Math.sqrt(Math.random())*u,j={node:c,x:x?x.x:Math.cos(V)*_t,y:x?x.y:Math.sin(V)*_t,vx:0,vy:0,r:8+Math.min(14,A*2.2),degree:A,fixed:!!x,el:this._makeNode(c,w,A),circle:null};j.circle=j.el.querySelector("circle"),this._particles.push(j),this._byId.set(c.id,j),s.appendChild(j.el)});for(let c of l){let _=this._byId.get(c.source),A=this._byId.get(c.target);if(!_||!A)continue;let w=document.createElementNS(Q,"line");w.setAttribute("class","edge"),w.setAttribute("marker-end","url(#sx-graph-arrow)"),t.appendChild(w);let x=null;c.label&&(x=document.createElementNS(Q,"text"),x.setAttribute("class","edge-label"),x.setAttribute("text-anchor","middle"),x.textContent=c.label,t.appendChild(x)),this._links.push({edge:c,a:_,b:A,line:w,label:x})}this._legend=[...v.entries()].map(([c,_])=>({label:c,color:_})),this._laidOut=!0,this._settle();for(let c of this._particles)c.fixed=!1;this._saveLayout(),this.fit(),this.requestUpdate()}_loadLayout(){if(!this.storageKey)return null;try{let t=localStorage.getItem(this.storageKey);if(!t)return null;let s=JSON.parse(t);return s&&typeof s=="object"?s:null}catch{return null}}_saveLayout(){if(!(!this.storageKey||this._particles.length===0))try{let t={};for(let s of this._particles)t[s.node.id]={x:Math.round(s.x),y:Math.round(s.y)};localStorage.setItem(this.storageKey,JSON.stringify(t))}catch{}}reorganize(){if(this.storageKey)try{localStorage.removeItem(this.storageKey)}catch{}this._build()}_makeNode(t,s,i){let r=document.createElementNS(Q,"g");r.setAttribute("class","node"),r.setAttribute("tabindex","0"),r.setAttribute("role","button"),r.setAttribute("aria-label",`${t.label}${t.category?` (${t.category})`:""}`),r.dataset.id=t.id;let o=document.createElementNS(Q,"circle"),l=8+Math.min(14,i*2.2);o.setAttribute("r",String(l)),o.setAttribute("fill",s),r.appendChild(o);let a=document.createElementNS(Q,"text");a.setAttribute("text-anchor","middle"),a.setAttribute("dy",String(-l-6));let d=t.label.length>28?`${t.label.slice(0,27)}\u2026`:t.label;return a.textContent=d,r.appendChild(a),r.addEventListener("keydown",h=>{(h.key==="Enter"||h.key===" ")&&(h.preventDefault(),this._select(t.id))}),r.addEventListener("pointerenter",()=>this._highlight(t.id)),r.addEventListener("pointerleave",()=>this._highlight(null)),r.addEventListener("focus",()=>this._highlight(t.id)),r.addEventListener("blur",()=>this._highlight(null)),r}_step(t){let s=this._particles,i=s.length,r=7e3,o=.012;for(let a=0;a<i;a+=1){let d=s[a];for(let h=a+1;h<i;h+=1){let u=s[h],v=d.x-u.x,c=d.y-u.y,_=v*v+c*c;_<.01&&(v=Math.random()-.5,c=Math.random()-.5,_=v*v+c*c);let A=Math.sqrt(_),w=Math.min(r/_,90),x=v/A*w,V=c/A*w;d.vx+=x,d.vy+=V,u.vx-=x,u.vy-=V}d.vx-=d.x*o,d.vy-=d.y*o}for(let a of this._links){let{a:d,b:h}=a,u=h.x-d.x,v=h.y-d.y,c=Math.sqrt(u*u+v*v)||1,_=150+d.r+h.r,A=(c-_)*.06,w=u/c*A,x=v/c*A;d.vx+=w,d.vy+=x,h.vx-=w,h.vy-=x}let l=.85;for(let a of s){if(a.fixed){a.vx=0,a.vy=0;continue}a.vx*=l,a.vy*=l,a.x+=a.vx*t,a.y+=a.vy*t}}_settle(){let t=1;for(let s=0;s<450&&t>.004;s+=1)this._step(t),t*=.985;this._draw()}_draw(){let t=this._viewport;t&&t.setAttribute("transform",`translate(${this._tx} ${this._ty}) scale(${this._k})`);for(let s of this._particles)s.el.setAttribute("transform",`translate(${s.x} ${s.y})`);for(let s of this._links){let{a:i,b:r,line:o,label:l}=s,a=r.x-i.x,d=r.y-i.y,h=Math.sqrt(a*a+d*d)||1,u=a/h,v=d/h;o.setAttribute("x1",String(i.x+u*i.r)),o.setAttribute("y1",String(i.y+v*i.r)),o.setAttribute("x2",String(r.x-u*(r.r+6))),o.setAttribute("y2",String(r.y-v*(r.r+6))),l&&(l.setAttribute("x",String((i.x+r.x)/2)),l.setAttribute("y",String((i.y+r.y)/2)))}}fit(){if(this._particles.length===0||this._width===0)return;let t=1/0,s=1/0,i=-1/0,r=-1/0;for(let h of this._particles)t=Math.min(t,h.x-h.r),s=Math.min(s,h.y-h.r),i=Math.max(i,h.x+h.r),r=Math.max(r,h.y+h.r);let o=48,l=i-t||1,a=r-s||1,d=Math.min((this._width-o*2)/l,(this._height-o*2)/a,1.6);this._k=Math.max(.1,d),this._tx=this._width/2-(t+i)/2*this._k,this._ty=this._height/2-(s+r)/2*this._k,this._draw()}_zoomBy(t,s,i){let r=s??this._width/2,o=i??this._height/2,l=Math.max(.1,Math.min(4,this._k*t));this._tx=r-(r-this._tx)*l/this._k,this._ty=o-(o-this._ty)*l/this._k,this._k=l,this._draw()}_toWorld(t,s){let i=this.getBoundingClientRect(),r=t-i.left,o=s-i.top;return{x:(r-this._tx)/this._k,y:(o-this._ty)/this._k}}_select(t){this.dispatchEvent(new CustomEvent("sx-entity-select",{detail:{id:t},bubbles:!0,composed:!0}))}_highlight(t){if(t===this._activeId)return;this._activeId=t;let s=this._svg;if(!s)return;if(!t){s.classList.remove("is-hovering");for(let r of this._particles)r.el.classList.remove("is-active");for(let r of this._links)r.line.classList.remove("is-active"),r.label?.classList.remove("is-active");return}let i=new Set([t]);for(let r of this._links){let o=r.a.node.id===t||r.b.node.id===t;r.line.classList.toggle("is-active",o),r.label?.classList.toggle("is-active",o),o&&(i.add(r.a.node.id),i.add(r.b.node.id))}for(let r of this._particles)r.el.classList.toggle("is-active",i.has(r.node.id));s.classList.add("is-hovering")}render(){return m`
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
      ${this._empty?m`<div class="empty">
            Aucune relation à afficher. Créez des entités et liez-les depuis le
            rail pour voir apparaître le graphe.
          </div>`:m`
            <div class="toolbar">
              <button type="button" title="Zoom avant" aria-label="Zoom avant" @click=${()=>this._zoomBy(1.2)}>+</button>
              <button type="button" title="Zoom arrière" aria-label="Zoom arrière" @click=${()=>this._zoomBy(1/1.2)}>−</button>
              <button type="button" title="Ajuster" aria-label="Ajuster la vue" @click=${()=>this.fit()}>⤢</button>
              <button type="button" title="Réorganiser" aria-label="Réorganiser le graphe" @click=${()=>this.reorganize()}>↻</button>
            </div>
            ${this._legend.length?m`<div class="legend">
                  ${this._legend.map(t=>m`<span><i style=${`background:${t.color}`}></i>${t.label}</span>`)}
                </div>`:null}
          `}
    `}};O.styles=b`
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
  `,p([f({attribute:!1})],O.prototype,"data",2),p([f({attribute:"storage-key"})],O.prototype,"storageKey",2),p([nt()],O.prototype,"_empty",2),O=p([y("sx-entity-graph")],O);var tt=class extends g{render(){return m`<div class="property" part="property">
      <span class="label" part="label"><slot name="label"></slot></span>
      <span class="value" part="value"><slot></slot></span>
      <span class="actions" part="actions"><slot name="actions"></slot></span>
    </div>`}};tt.styles=b`
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
  `,tt=p([y("sx-property")],tt);var oe={tiktok:{color:"#EE1D52",path:"M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"},instagram:{color:"#E4405F",path:"M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077"},x:{color:"currentColor",path:"M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z"},facebook:{color:"#1877F2",path:"M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z"},youtube:{color:"#FF0000",path:"M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"},googlemaps:{color:"#1A73E8",path:"M19.527 4.799c1.212 2.608.937 5.678-.405 8.173-1.101 2.047-2.744 3.74-4.098 5.614-.619.858-1.244 1.75-1.669 2.727-.141.325-.263.658-.383.992-.121.333-.224.673-.34 1.008-.109.314-.236.684-.627.687h-.007c-.466-.001-.579-.53-.695-.887-.284-.874-.581-1.713-1.019-2.525-.51-.944-1.145-1.817-1.79-2.671L19.527 4.799zM8.545 7.705l-3.959 4.707c.724 1.54 1.821 2.863 2.871 4.18.247.31.494.622.737.936l4.984-5.925-.029.01c-1.741.601-3.691-.291-4.392-1.987a3.377 3.377 0 0 1-.209-.716c-.063-.437-.077-.761-.004-1.198l.001-.007zM5.492 3.149l-.003.004c-1.947 2.466-2.281 5.88-1.117 8.77l4.785-5.689-.058-.05-3.607-3.035zM14.661.436l-3.838 4.563a.295.295 0 0 1 .027-.01c1.6-.551 3.403.15 4.22 1.626.176.319.323.683.377 1.045.068.446.085.773.012 1.22l-.003.016 3.836-4.561A8.382 8.382 0 0 0 14.67.439l-.009-.003zM9.466 5.868L14.162.285l-.047-.012A8.31 8.31 0 0 0 11.986 0a8.439 8.439 0 0 0-6.169 2.766l-.016.018 3.665 3.084z"},telegram:{color:"#229ED9",path:"M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"},snapchat:{color:"#E0A800",path:"M12.206.793c.99 0 4.347.276 5.93 3.821.529 1.193.403 3.219.299 4.847l-.003.06c-.012.18-.022.345-.03.51.075.045.203.09.401.09.3-.016.659-.12 1.033-.301.165-.088.344-.104.464-.104.182 0 .359.029.509.09.45.149.734.479.734.838.015.449-.39.839-1.213 1.168-.089.029-.209.075-.344.119-.45.135-1.139.36-1.333.81-.09.224-.061.524.12.868l.015.015c.06.136 1.526 3.475 4.791 4.014.255.044.435.27.42.509 0 .075-.015.149-.045.225-.24.569-1.273.988-3.146 1.271-.059.091-.12.375-.164.57-.029.179-.074.36-.134.553-.076.271-.27.405-.555.405h-.03c-.135 0-.313-.031-.538-.074-.36-.075-.765-.135-1.273-.135-.3 0-.599.015-.913.074-.6.104-1.123.464-1.723.884-.853.599-1.826 1.288-3.294 1.288-.06 0-.119-.015-.18-.015h-.149c-1.468 0-2.427-.675-3.279-1.288-.599-.42-1.107-.779-1.707-.884-.314-.045-.629-.074-.928-.074-.54 0-.958.089-1.272.149-.211.043-.391.074-.54.074-.374 0-.523-.224-.583-.42-.061-.192-.09-.389-.135-.567-.046-.181-.105-.494-.166-.57-1.918-.222-2.95-.642-3.189-1.226-.031-.063-.052-.15-.055-.225-.015-.243.165-.465.42-.509 3.264-.54 4.73-3.879 4.791-4.02l.016-.029c.18-.345.224-.645.119-.869-.195-.434-.884-.658-1.332-.809-.121-.029-.24-.074-.346-.119-1.107-.435-1.257-.93-1.197-1.273.09-.479.674-.793 1.168-.793.146 0 .27.029.383.074.42.194.789.3 1.104.3.234 0 .384-.06.465-.105l-.046-.569c-.098-1.626-.225-3.651.307-4.837C7.392 1.077 10.739.807 11.727.807l.419-.015h.06z"},pinterest:{color:"#BD081C",path:"M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.162-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.401.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.354-.629-2.758-1.379l-.749 2.848c-.269 1.045-1.004 2.352-1.498 3.146 1.123.345 2.306.535 3.55.535 6.607 0 11.985-5.365 11.985-11.987C23.97 5.39 18.592.026 11.985.026L12.017 0z"},reddit:{color:"#FF4500",path:"M12 0C5.373 0 0 5.373 0 12c0 3.314 1.343 6.314 3.515 8.485l-2.286 2.286C.775 23.225 1.097 24 1.738 24H12c6.627 0 12-5.373 12-12S18.627 0 12 0Zm4.388 3.199c1.104 0 1.999.895 1.999 1.999 0 1.105-.895 2-1.999 2-.946 0-1.739-.657-1.947-1.539v.002c-1.147.162-2.032 1.15-2.032 2.341v.007c1.776.067 3.4.567 4.686 1.363.473-.363 1.064-.58 1.707-.58 1.547 0 2.802 1.254 2.802 2.802 0 1.117-.655 2.081-1.601 2.531-.088 3.256-3.637 5.876-7.997 5.876-4.361 0-7.905-2.617-7.998-5.87-.954-.447-1.614-1.415-1.614-2.538 0-1.548 1.255-2.802 2.803-2.802.645 0 1.239.218 1.712.585 1.275-.79 2.881-1.291 4.64-1.365v-.01c0-1.663 1.263-3.034 2.88-3.207.188-.911.993-1.595 1.959-1.595Zm-8.085 8.376c-.784 0-1.459.78-1.506 1.797-.047 1.016.64 1.429 1.426 1.429.786 0 1.371-.369 1.418-1.385.047-1.017-.553-1.841-1.338-1.841Zm7.406 0c-.786 0-1.385.824-1.338 1.841.047 1.017.634 1.385 1.418 1.385.785 0 1.473-.413 1.426-1.429-.046-1.017-.721-1.797-1.506-1.797Zm-3.703 4.013c-.974 0-1.907.048-2.77.135-.147.015-.241.168-.183.305.483 1.154 1.622 1.964 2.953 1.964 1.33 0 2.47-.81 2.953-1.964.057-.137-.037-.29-.184-.305-.863-.087-1.795-.135-2.769-.135Z"},whatsapp:{color:"#25D366",path:"M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"}},Gt=["#38bdf8","#a78bfa","#34d399","#fbbf24","#f472b6","#22d3ee","#c084fc","#fb7185"],k=class extends g{constructor(){super(...arguments);this.observations=0;this.firstSeen="";this.lastSeen="";this.initial="";this.site="";this.imported=!1;this._menuOpen=!1;this._toggleMenu=t=>{t.stopPropagation(),this._menuOpen?this._closeMenu():this._openMenu()};this._onDocPointerDown=t=>{t.composedPath().includes(this)||this._closeMenu()};this._onKeyDown=t=>{t.key==="Escape"&&this._menuOpen&&(t.stopPropagation(),this._closeMenu())};this._onMenuClick=()=>{this._closeMenu()}}connectedCallback(){super.connectedCallback(),this.addEventListener("keydown",this._onKeyDown)}disconnectedCallback(){super.disconnectedCallback(),this.removeEventListener("keydown",this._onKeyDown),document.removeEventListener("pointerdown",this._onDocPointerDown,!0)}_openMenu(){this._menuOpen=!0,this.toggleAttribute("menu-open",!0),document.addEventListener("pointerdown",this._onDocPointerDown,!0)}_closeMenu(){this._menuOpen&&(this._menuOpen=!1,this.toggleAttribute("menu-open",!1),document.removeEventListener("pointerdown",this._onDocPointerDown,!0))}_brand(){let t=this.site.trim().toLowerCase();if(!t)return null;let i={"t.me":"telegram","telegram.org":"telegram","wa.me":"whatsapp","youtu.be":"youtube","fb.com":"facebook","x.com":"x","twitter.com":"x"}[t];if(!i){let r=t.split(".").filter(Boolean),o=r.length>=2?r[r.length-2]:r[0]??"";i={twitter:"x",google:"googlemaps"}[o]??o}return oe[i]??null}get _faviconColor(){let t=(this.site||this.initial||"").toLowerCase();if(!t)return"var(--accent, #6366f1)";let s=0;for(let i=0;i<t.length;i+=1)s=s*31+t.charCodeAt(i)|0;return Gt[Math.abs(s)%Gt.length]}_fmt(t,s){if(!t)return"";let i=new Date(t.replace(/(\.\d{3})\d+/,"$1"));return Number.isNaN(i.getTime())?"":new Intl.DateTimeFormat(void 0,s).format(i)}_renderFavicon(){let t=this.imported?"Document import\xE9":this.site,s=m`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
      stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 3v4a1 1 0 0 0 1 1h4"></path>
      <path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2Z"></path>
    </svg>`;if(this.imported){let l=this._faviconColor,a=`background: color-mix(in srgb, ${l} 18%, transparent); color: ${l};`;return m`<span class="favicon" style=${a} title=${t} aria-hidden="true">${s}</span>`}let i=this._brand();if(i){let l=i.color==="currentColor",a=l?"var(--text, #e2e8f0)":i.color,h=`background: color-mix(in srgb, ${l?"var(--muted, #94a3b8)":i.color} 18%, transparent); color: ${a};`;return m`<span class="favicon" style=${h} title=${t} aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d=${i.path}></path></svg>
      </span>`}let r=this._faviconColor,o=`background: color-mix(in srgb, ${r} 18%, transparent); color: ${r};`;return m`<span class="favicon" style=${o} title=${t} aria-hidden="true">${this.initial||"\xB7"}</span>`}_renderSeenPill(){let t={day:"numeric",month:"short"},s={dateStyle:"medium",timeStyle:"short"},i=this._fmt(this.firstSeen,t),r=this._fmt(this.lastSeen,t);if(!i&&!r)return null;let o=i&&r&&i!==r?`${i} \u2192 ${r}`:r||i,l=this._fmt(this.firstSeen,s),a=this._fmt(this.lastSeen,s),d=[l?`Premi\xE8re observation : ${l}`:"",a?`Derni\xE8re observation : ${a}`:""].filter(Boolean).join(" \xB7 ");return m`<span class="pill" title=${d} aria-label=${d}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="9"></circle>
        <path d="M12 7v5l3 2"></path>
      </svg>
      ${o}
    </span>`}render(){let t=Number(this.observations)||0,s=`${t} observation${t===1?"":"s"}`;return m`
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
    `}};k.styles=b`
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
  `,p([f({type:Number})],k.prototype,"observations",2),p([f({attribute:"first-seen"})],k.prototype,"firstSeen",2),p([f({attribute:"last-seen"})],k.prototype,"lastSeen",2),p([f()],k.prototype,"initial",2),p([f()],k.prototype,"site",2),p([f({type:Boolean})],k.prototype,"imported",2),p([nt()],k.prototype,"_menuOpen",2),k=p([y("sx-saved-page-card")],k);})();
