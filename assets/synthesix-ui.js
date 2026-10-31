"use strict";(()=>{var Pe=Object.defineProperty;var Me=Object.getOwnPropertyDescriptor;var p=(i,e,t,s)=>{for(var r=s>1?void 0:s?Me(e,t):e,o=i.length-1,n;o>=0;o--)(n=i[o])&&(r=(s?n(e,t,r):n(r))||r);return s&&r&&Pe(e,t,r),r};var Q=globalThis,Y=Q.ShadowRoot&&(Q.ShadyCSS===void 0||Q.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,X=Symbol(),de=new WeakMap,N=class{constructor(e,t,s){if(this._$cssResult$=!0,s!==X)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(Y&&e===void 0){let s=t!==void 0&&t.length===1;s&&(e=de.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),s&&de.set(t,e))}return e}toString(){return this.cssText}},he=i=>new N(typeof i=="string"?i:i+"",void 0,X),$=(i,...e)=>{let t=i.length===1?i[0]:e.reduce((s,r,o)=>s+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+i[o+1],i[0]);return new N(t,i,X)},ue=(i,e)=>{if(Y)i.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let s=document.createElement("style"),r=Q.litNonce;r!==void 0&&s.setAttribute("nonce",r),s.textContent=t.cssText,i.appendChild(s)}},ee=Y?i=>i:i=>i instanceof CSSStyleSheet?(e=>{let t="";for(let s of e.cssRules)t+=s.cssText;return he(t)})(i):i;var{is:Te,defineProperty:Le,getOwnPropertyDescriptor:Re,getOwnPropertyNames:Ue,getOwnPropertySymbols:Ne,getPrototypeOf:He}=Object,G=globalThis,me=G.trustedTypes,Oe=me?me.emptyScript:"",ze=G.reactiveElementPolyfillSupport,H=(i,e)=>i,O={toAttribute(i,e){switch(e){case Boolean:i=i?Oe:null;break;case Object:case Array:i=i==null?i:JSON.stringify(i)}return i},fromAttribute(i,e){let t=i;switch(e){case Boolean:t=i!==null;break;case Number:t=i===null?null:Number(i);break;case Object:case Array:try{t=JSON.parse(i)}catch{t=null}}return t}},K=(i,e)=>!Te(i,e),fe={attribute:!0,type:String,converter:O,reflect:!1,useDefault:!1,hasChanged:K};Symbol.metadata??=Symbol("metadata"),G.litPropertyMetadata??=new WeakMap;var _=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=fe){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let s=Symbol(),r=this.getPropertyDescriptor(e,s,t);r!==void 0&&Le(this.prototype,e,r)}}static getPropertyDescriptor(e,t,s){let{get:r,set:o}=Re(this.prototype,e)??{get(){return this[t]},set(n){this[t]=n}};return{get:r,set(n){let c=r?.call(this);o?.call(this,n),this.requestUpdate(e,c,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??fe}static _$Ei(){if(this.hasOwnProperty(H("elementProperties")))return;let e=He(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(H("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(H("properties"))){let t=this.properties,s=[...Ue(t),...Ne(t)];for(let r of s)this.createProperty(r,t[r])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[s,r]of t)this.elementProperties.set(s,r)}this._$Eh=new Map;for(let[t,s]of this.elementProperties){let r=this._$Eu(t,s);r!==void 0&&this._$Eh.set(r,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let s=new Set(e.flat(1/0).reverse());for(let r of s)t.unshift(ee(r))}else e!==void 0&&t.push(ee(e));return t}static _$Eu(e,t){let s=t.attribute;return s===!1?void 0:typeof s=="string"?s:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let s of t.keys())this.hasOwnProperty(s)&&(e.set(s,this[s]),delete this[s]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return ue(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,s){this._$AK(e,s)}_$ET(e,t){let s=this.constructor.elementProperties.get(e),r=this.constructor._$Eu(e,s);if(r!==void 0&&s.reflect===!0){let o=(s.converter?.toAttribute!==void 0?s.converter:O).toAttribute(t,s.type);this._$Em=e,o==null?this.removeAttribute(r):this.setAttribute(r,o),this._$Em=null}}_$AK(e,t){let s=this.constructor,r=s._$Eh.get(e);if(r!==void 0&&this._$Em!==r){let o=s.getPropertyOptions(r),n=typeof o.converter=="function"?{fromAttribute:o.converter}:o.converter?.fromAttribute!==void 0?o.converter:O;this._$Em=r;let c=n.fromAttribute(t,o.type);this[r]=c??this._$Ej?.get(r)??c,this._$Em=null}}requestUpdate(e,t,s,r=!1,o){if(e!==void 0){let n=this.constructor;if(r===!1&&(o=this[e]),s??=n.getPropertyOptions(e),!((s.hasChanged??K)(o,t)||s.useDefault&&s.reflect&&o===this._$Ej?.get(e)&&!this.hasAttribute(n._$Eu(e,s))))return;this.C(e,t,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:s,reflect:r,wrapped:o},n){s&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,n??t??this[e]),o!==!0||n!==void 0)||(this._$AL.has(e)||(this.hasUpdated||s||(t=void 0),this._$AL.set(e,t)),r===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[r,o]of this._$Ep)this[r]=o;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[r,o]of s){let{wrapped:n}=o,c=this[r];n!==!0||this._$AL.has(r)||c===void 0||this.C(r,void 0,o,c)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(t)):this._$EM()}catch(s){throw e=!1,this._$EM(),s}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};_.elementStyles=[],_.shadowRootOptions={mode:"open"},_[H("elementProperties")]=new Map,_[H("finalized")]=new Map,ze?.({ReactiveElement:_}),(G.reactiveElementVersions??=[]).push("2.1.2");var ae=globalThis,ge=i=>i,J=ae.trustedTypes,ve=J?J.createPolicy("lit-html",{createHTML:i=>i}):void 0,_e="$lit$",k=`lit$${Math.random().toFixed(9).slice(2)}$`,ke="?"+k,De=`<${ke}>`,C=document,D=()=>C.createComment(""),j=i=>i===null||typeof i!="object"&&typeof i!="function",le=Array.isArray,je=i=>le(i)||typeof i?.[Symbol.iterator]=="function",te=`[ 	
\f\r]`,z=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,xe=/-->/g,be=/>/g,A=RegExp(`>|${te}(?:([^\\s"'>=/]+)(${te}*=${te}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),$e=/'/g,ye=/"/g,Ee=/^(?:script|style|textarea|title)$/i,ce=i=>(e,...t)=>({_$litType$:i,strings:e,values:t}),l=ce(1),F=ce(2),Xe=ce(3),q=Symbol.for("lit-noChange"),h=Symbol.for("lit-nothing"),we=new WeakMap,S=C.createTreeWalker(C,129);function Ae(i,e){if(!le(i)||!i.hasOwnProperty("raw"))throw Error("invalid template strings array");return ve!==void 0?ve.createHTML(e):e}var Ie=(i,e)=>{let t=i.length-1,s=[],r,o=e===2?"<svg>":e===3?"<math>":"",n=z;for(let c=0;c<t;c++){let a=i[c],m,f,u=-1,d=0;for(;d<a.length&&(n.lastIndex=d,f=n.exec(a),f!==null);)d=n.lastIndex,n===z?f[1]==="!--"?n=xe:f[1]!==void 0?n=be:f[2]!==void 0?(Ee.test(f[2])&&(r=RegExp("</"+f[2],"g")),n=A):f[3]!==void 0&&(n=A):n===A?f[0]===">"?(n=r??z,u=-1):f[1]===void 0?u=-2:(u=n.lastIndex-f[2].length,m=f[1],n=f[3]===void 0?A:f[3]==='"'?ye:$e):n===ye||n===$e?n=A:n===xe||n===be?n=z:(n=A,r=void 0);let x=n===A&&i[c+1].startsWith("/>")?" ":"";o+=n===z?a+De:u>=0?(s.push(m),a.slice(0,u)+_e+a.slice(u)+k+x):a+k+(u===-2?c:x)}return[Ae(i,o+(i[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),s]},I=class i{constructor({strings:e,_$litType$:t},s){let r;this.parts=[];let o=0,n=0,c=e.length-1,a=this.parts,[m,f]=Ie(e,t);if(this.el=i.createElement(m,s),S.currentNode=this.el.content,t===2||t===3){let u=this.el.content.firstChild;u.replaceWith(...u.childNodes)}for(;(r=S.nextNode())!==null&&a.length<c;){if(r.nodeType===1){if(r.hasAttributes())for(let u of r.getAttributeNames())if(u.endsWith(_e)){let d=f[n++],x=r.getAttribute(u).split(k),T=/([.?@])?(.*)/.exec(d);a.push({type:1,index:o,name:T[2],strings:x,ctor:T[1]==="."?re:T[1]==="?"?ie:T[1]==="@"?oe:R}),r.removeAttribute(u)}else u.startsWith(k)&&(a.push({type:6,index:o}),r.removeAttribute(u));if(Ee.test(r.tagName)){let u=r.textContent.split(k),d=u.length-1;if(d>0){r.textContent=J?J.emptyScript:"";for(let x=0;x<d;x++)r.append(u[x],D()),S.nextNode(),a.push({type:2,index:++o});r.append(u[d],D())}}}else if(r.nodeType===8)if(r.data===ke)a.push({type:2,index:o});else{let u=-1;for(;(u=r.data.indexOf(k,u+1))!==-1;)a.push({type:7,index:o}),u+=k.length-1}o++}}static createElement(e,t){let s=C.createElement("template");return s.innerHTML=e,s}};function L(i,e,t=i,s){if(e===q)return e;let r=s!==void 0?t._$Co?.[s]:t._$Cl,o=j(e)?void 0:e._$litDirective$;return r?.constructor!==o&&(r?._$AO?.(!1),o===void 0?r=void 0:(r=new o(i),r._$AT(i,t,s)),s!==void 0?(t._$Co??=[])[s]=r:t._$Cl=r),r!==void 0&&(e=L(i,r._$AS(i,e.values),r,s)),e}var se=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:s}=this._$AD,r=(e?.creationScope??C).importNode(t,!0);S.currentNode=r;let o=S.nextNode(),n=0,c=0,a=s[0];for(;a!==void 0;){if(n===a.index){let m;a.type===2?m=new B(o,o.nextSibling,this,e):a.type===1?m=new a.ctor(o,a.name,a.strings,this,e):a.type===6&&(m=new ne(o,this,e)),this._$AV.push(m),a=s[++c]}n!==a?.index&&(o=S.nextNode(),n++)}return S.currentNode=C,r}p(e){let t=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(e,s,t),t+=s.strings.length-2):s._$AI(e[t])),t++}},B=class i{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,s,r){this.type=2,this._$AH=h,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=s,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=L(this,e,t),j(e)?e===h||e==null||e===""?(this._$AH!==h&&this._$AR(),this._$AH=h):e!==this._$AH&&e!==q&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):je(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==h&&j(this._$AH)?this._$AA.nextSibling.data=e:this.T(C.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:s}=e,r=typeof s=="number"?this._$AC(e):(s.el===void 0&&(s.el=I.createElement(Ae(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===r)this._$AH.p(t);else{let o=new se(r,this),n=o.u(this.options);o.p(t),this.T(n),this._$AH=o}}_$AC(e){let t=we.get(e.strings);return t===void 0&&we.set(e.strings,t=new I(e)),t}k(e){le(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,s,r=0;for(let o of e)r===t.length?t.push(s=new i(this.O(D()),this.O(D()),this,this.options)):s=t[r],s._$AI(o),r++;r<t.length&&(this._$AR(s&&s._$AB.nextSibling,r),t.length=r)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let s=ge(e).nextSibling;ge(e).remove(),e=s}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},R=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,s,r,o){this.type=1,this._$AH=h,this._$AN=void 0,this.element=e,this.name=t,this._$AM=r,this.options=o,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=h}_$AI(e,t=this,s,r){let o=this.strings,n=!1;if(o===void 0)e=L(this,e,t,0),n=!j(e)||e!==this._$AH&&e!==q,n&&(this._$AH=e);else{let c=e,a,m;for(e=o[0],a=0;a<o.length-1;a++)m=L(this,c[s+a],t,a),m===q&&(m=this._$AH[a]),n||=!j(m)||m!==this._$AH[a],m===h?e=h:e!==h&&(e+=(m??"")+o[a+1]),this._$AH[a]=m}n&&!r&&this.j(e)}j(e){e===h?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},re=class extends R{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===h?void 0:e}},ie=class extends R{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==h)}},oe=class extends R{constructor(e,t,s,r,o){super(e,t,s,r,o),this.type=5}_$AI(e,t=this){if((e=L(this,e,t,0)??h)===q)return;let s=this._$AH,r=e===h&&s!==h||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,o=e!==h&&(s===h||r);r&&this.element.removeEventListener(this.name,this,s),o&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},ne=class{constructor(e,t,s){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(e){L(this,e)}};var Be=ae.litHtmlPolyfillSupport;Be?.(I,B),(ae.litHtmlVersions??=[]).push("3.3.3");var Se=(i,e,t)=>{let s=t?.renderBefore??e,r=s._$litPart$;if(r===void 0){let o=t?.renderBefore??null;s._$litPart$=r=new B(e.insertBefore(D(),o),o,void 0,t??{})}return r._$AI(i),r};var pe=globalThis,g=class extends _{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Se(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return q}};g._$litElement$=!0,g.finalized=!0,pe.litElementHydrateSupport?.({LitElement:g});var Fe=pe.litElementPolyfillSupport;Fe?.({LitElement:g});(pe.litElementVersions??=[]).push("4.2.2");var y=i=>(e,t)=>{t!==void 0?t.addInitializer(()=>{customElements.define(i,e)}):customElements.define(i,e)};var Ve={attribute:!0,type:String,converter:O,reflect:!1,hasChanged:K},We=(i=Ve,e,t)=>{let{kind:s,metadata:r}=t,o=globalThis.litPropertyMetadata.get(r);if(o===void 0&&globalThis.litPropertyMetadata.set(r,o=new Map),s==="setter"&&((i=Object.create(i)).wrapped=!0),o.set(t.name,i),s==="accessor"){let{name:n}=t;return{set(c){let a=e.get.call(this);e.set.call(this,c),this.requestUpdate(n,a,i,!0,c)},init(c){return c!==void 0&&this.C(n,void 0,i,c),c}}}if(s==="setter"){let{name:n}=t;return function(c){let a=this[n];e.call(this,c),this.requestUpdate(n,a,i,!0,c)}}throw Error("Unsupported decorator location: "+s)};function b(i){return(e,t)=>typeof t=="object"?We(i,e,t):((s,r,o)=>{let n=r.hasOwnProperty(o);return r.constructor.createProperty(o,s),n?Object.getOwnPropertyDescriptor(r,o):void 0})(i,e,t)}function w(i){return b({...i,state:!0,attribute:!1})}var U=class extends g{constructor(){super(...arguments);this.tone="neutral"}render(){return l`<span class="chip"><slot></slot></span>`}};U.styles=$`
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
  `,p([b({reflect:!0})],U.prototype,"tone",2),U=p([y("sx-chip")],U);var V=[["google","Google"],["bing","Bing"],["brave","Brave"],["duckduckgo","DuckDuckGo"]],Ce=20,Qe=8,v=class extends g{constructor(){super(...arguments);this.model={connected:!1,running:!1,results:[],profiles:[],history:[],coverage:[],status:"Starting Synthesix...",isError:!1};this.queries="";this.engines={google:!0,bing:!0,brave:!0,duckduckgo:!0};this.filters={};this.automatic=!0;this.count=20;this.selectedProfile="";this.filterText="";this.source="";this.visible=100;this.tab="search";this.profileName="";this.observer=new MutationObserver(()=>this.requestUpdate())}connectedCallback(){super.connectedCallback(),this.observer.observe(document.documentElement,{attributes:!0,attributeFilter:["lang","data-theme"]})}disconnectedCallback(){this.observer.disconnect(),super.disconnectedCallback()}updated(t){let s=t.get("model");if(t.has("model")&&this.model.request&&this.model.request!==s?.request){let r=this.model.request;this.queries=r.queries.join(`
`),this.engines={...r.engines},this.filters={...r.filters},this.automatic=r.automaticDorks,this.count=r.numResults,this.tab="search"}}t(t){return window.synthesixI18n?.t(t)??t}locale(){return document.documentElement.lang||"fr"}send(t,s={}){this.dispatchEvent(new CustomEvent("sx-browser-action",{detail:{action:t,...s},bubbles:!0,composed:!0}))}search(t){t.preventDefault(),this.visible=100,this.filterText="",this.source="",this.send("search",{queries:this.queries.split(`
`).map(s=>s.trim()).filter(Boolean),engines:this.engines,filters:this.filters,numResults:this.count,automaticDorks:this.automatic})}field(t,s,r="text"){return l`<label>${this.t(s)}<input type=${r} name=${t} maxlength="500" autocomplete="off" spellcheck="false" .value=${this.filters[t]??""} @input=${o=>{this.filters={...this.filters,[t]:o.target.value}}}></label>`}safeUrl(t){try{let s=new URL(t);return["http:","https:"].includes(s.protocol)&&!s.username&&!s.password?s.href:""}catch{return""}}splitUrl(t){try{let s=new URL(t);return{host:s.hostname.replace(/^www\./,""),path:`${s.pathname==="/"?"":s.pathname}${s.search}`}}catch{return{host:t,path:""}}}open(t,s){t.preventDefault(),this.safeUrl(s.link)&&this.send("open_result",{url:s.link,profileId:this.selectedProfile})}icon(t){let s={search:F`<circle cx="7" cy="7" r="4.5"/><path d="m10.5 10.5 3 3"/>`,sun:F`<circle cx="8" cy="8" r="3"/><path d="M8 1.5v1.5M8 13v1.5M1.5 8H3M13 8h1.5M3.4 3.4l1 1M11.6 11.6l1 1M3.4 12.6l1-1M11.6 4.4l1-1"/>`,moon:F`<path d="M13.5 9.5A5.5 5.5 0 0 1 6.5 2.5a5.5 5.5 0 1 0 7 7Z"/>`,external:F`<path d="M9.5 2.5h4v4M13.5 2.5 8 8M12 9.5v4H2.5V4h4"/>`};return l`<svg class="icon" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">${s[t]}</svg>`}profileSelect(){return l`<label class="profile-picker">${this.t("Open results with")}<select .value=${this.selectedProfile} @change=${t=>{this.selectedProfile=t.target.value}}><option value="">${this.t("Neutral profile")}</option>${this.model.profiles.map(t=>l`<option value=${t.id}>${t.name}</option>`)}</select></label>`}composer(){let t=new Set(this.queries.split(`
`).map(o=>o.trim()).filter(Boolean)).size,s=V.filter(([o])=>this.engines[o]).length,r=Object.values(this.filters).filter(o=>o.trim()).length;return l`<aside><form @submit=${this.search}>
      <h2>${this.t("Build your search")}</h2>
      <div class="group">
        <div class="label-row"><label for="queries">${this.t("Queries")}</label><span class=${t>Ce?"counter over":"counter"}>${t} / ${Ce}</span></div>
        <textarea id="queries" name="queries" rows="6" required maxlength="10020" spellcheck="false" autocomplete="off" translate="no" .value=${this.queries} @input=${o=>{this.queries=o.target.value}} placeholder=${this.t("One query per line")}></textarea>
        <label class="check"><input type="checkbox" .checked=${this.automatic} @change=${o=>{this.automatic=o.target.checked}}>${this.t("Automatic exact-phrase dorks")}</label>
      </div>
      <fieldset><legend>${this.t("Search engines")}</legend><div class="engine-grid">${V.map(([o,n])=>l`<label class="engine"><input type="checkbox" name=${o} .checked=${!!this.engines[o]} @change=${c=>{this.engines={...this.engines,[o]:c.target.checked}}}><span translate="no">${n}</span></label>`)}</div></fieldset>
      <details><summary>${this.t("Dork filters")}${r?l`<span class="badge">${r}</span>`:h}</summary><div class="fields">${this.field("site","Site")}${this.field("exclude","Exclude")}${this.field("filetype","File type")}${this.field("title","Title contains")}${this.field("url","URL contains")}${this.field("body","Page contains")}${this.field("country","Country code")}${this.field("after","After","date")}${this.field("before","Before","date")}</div></details>
      <label class="count">${this.t("Results per engine")}<input type="number" min="1" max="100" inputmode="numeric" .value=${String(this.count)} @change=${o=>{this.count=Number(o.target.value)}}></label>
      <div class="submit">
        <p class="plan"><strong>${t*s}</strong> ${this.t("engine requests")} <span>(${t} × ${s})</span></p>
        <button class="primary" type="submit" ?disabled=${!this.model.connected||this.model.running}>${this.t("Search")}</button>
        ${this.model.running?l`<button type="button" @click=${()=>this.send("cancel_search")}>${this.t("Cancel search")}</button>`:h}
      </div>
      <p class="hint">${this.t("Queries are merged into one deduplicated result list.")}</p>
    </form></aside>`}coverage(t,s,r){let o=this.model.coverage.reduce((n,c)=>n+Object.values(c.engines).filter(a=>a.status!=="ok").length,0);return l`<details class="coverage"><summary>${this.t("Search coverage")}<span class="figure">${s} / ${r}</span>${o?l`<span class="pill bad">${o} ${this.t("failed")}</span>`:h}</summary>
      <div class="table-wrap"><table><thead><tr><th scope="col">${this.t("Queries")}</th>${t.map(([,n])=>l`<th scope="col" class="num" translate="no">${n}</th>`)}</tr></thead>
      <tbody>${this.model.coverage.map(n=>l`<tr><th scope="row"><code translate="no" title=${n.query}>${n.query}</code></th>${t.map(([c])=>{let a=n.engines[c];return l`<td class="num">${a?a.status==="ok"?a.count:l`<span class="pill bad">${this.t(a.status)}</span>`:l`<span class="dim">${this.model.running?"\u2026":"\u2014"}</span>`}</td>`})}</tr>`)}</tbody></table></div></details>`}resultRow(t,s,r){let{host:o,path:n}=this.splitUrl(t.link),c=t.relevance_score;return l`<article>
      <div class="where" title=${t.link}><span class="host" translate="no">${o}</span><span class="path">${n}</span></div>
      <h2><a href=${this.safeUrl(t.link)||h} @click=${a=>this.open(a,t)}>${t.title||t.link}</a></h2>
      ${c!=null?l`<div class=${c>=Qe?"score strong":"score"} title=${this.t("Relevance")}>${r.format(c)}</div>`:h}
      ${t.description?l`<p class="desc">${t.description}</p>`:h}
      <div class="meta">${t.source.split(",").map(a=>l`<span class="tag" translate="no">${a.trim()}</span>`)}${s&&t.query_variants?.length?l`<span class="via">${this.t("Found via")}</span>${t.query_variants.map(a=>l`<code translate="no">${a}</code>`)}`:h}</div>
    </article>`}results(){let t=this.filterText.toLocaleLowerCase(),s=this.model.results,r=s.filter(d=>`${d.title} ${d.description??""} ${d.link}`.toLocaleLowerCase().includes(t)),o=r.filter(d=>!this.source||d.source.toLowerCase().includes(this.source)),n=V.filter(([d])=>(this.model.request?.engines??this.engines)[d]),c=V.filter(([d])=>n.some(([x])=>x===d)||s.some(x=>x.source.toLowerCase().includes(d))),a=this.model.coverage.reduce((d,x)=>d+Object.keys(x.engines).length,0),m=this.model.coverage.length*n.length,f=new Intl.NumberFormat(this.locale(),{minimumFractionDigits:1,maximumFractionDigits:1}),u=(this.model.request?.queries.length??0)>1;return l`<section class="results" aria-busy=${String(this.model.running)}>
      <div class="heading"><div><h1>${this.t("Search results")} <span class="total">${s.length}</span></h1>
        <p class=${this.model.isError?"status error":"status"} role="status" aria-live="polite">${this.t(this.model.status)}${m?l`<span class="progress">${a} / ${m} ${this.t("engine requests completed")}</span>`:h}</p></div>
        ${this.profileSelect()}</div>
      ${this.model.running&&m?l`<progress max=${m} .value=${a} aria-label=${this.t("engine requests completed")}></progress>`:h}
      ${s.length?l`<div class="tools"><label class="search-field">${this.icon("search")}<input aria-label=${this.t("Filter results")} placeholder=${this.t("Filter results")} type="search" autocomplete="off" .value=${this.filterText} @input=${d=>{this.filterText=d.target.value,this.visible=100}}></label><div class="chips" role="group" aria-label=${this.t("Filter by engine")}>${[["",this.t("All engines")],...c].map(([d,x])=>l`<button type="button" class="chip" aria-pressed=${String(this.source===d)} @click=${()=>{this.source=d,this.visible=100}}><span translate="no">${x}</span><span class="n">${d?r.filter(T=>T.source.toLowerCase().includes(d)).length:r.length}</span></button>`)}</div></div>`:h}
      ${this.model.coverage.length?this.coverage(n,a,m):h}
      ${o.length?l`<div class="result-list"><div class="list-head" aria-hidden="true">${this.t("Relevance")}</div>${o.slice(0,this.visible).map(d=>this.resultRow(d,u,f))}</div>${o.length>this.visible?l`<button class="more" @click=${()=>{this.visible+=100}}>${this.t("Show more results")}</button>`:h}`:l`<div class="empty"><h2>${this.t(s.length?"No results match this filter.":this.model.running?"Searching selected engines...":"Your next search starts here.")}</h2><p>${this.t("Write your queries on the left, choose your engines, then search.")}</p></div>`}
    </section>`}profiles(){return l`<section class="secondary"><h1>${this.t("Browser profiles")}</h1><p class="lede">${this.t("Each profile keeps its own website logins. Sign in once in its browser window.")}</p>
      <form class="inline-form" @submit=${t=>{t.preventDefault(),this.send("create_profile",{name:this.profileName}),this.profileName=""}}><label>${this.t("Profile name")}<input required maxlength="80" autocomplete="off" .value=${this.profileName} @input=${t=>{this.profileName=t.target.value}}></label><button class="primary" ?disabled=${!this.model.connected}>${this.t("Create profile")}</button></form>
      <p class=${this.model.isError?"status error":"status"} role="status">${this.t(this.model.status)}</p>
      ${this.model.profiles.length?l`<ul class="rows">${this.model.profiles.map(t=>l`<li><form class="profile-row" @submit=${s=>{s.preventDefault();let r=new FormData(s.target);this.send("rename_profile",{profileId:t.id,name:r.get("name")})}}>
        <span class="avatar" style="--hue:${[...t.id].reduce((s,r)=>(s*31+r.charCodeAt(0))%360,7)}" aria-hidden="true">${[...t.name.trim()][0]?.toLocaleUpperCase()??"?"}</span>
        <label class="sr-only" for=${t.id}>${this.t("Profile name")}</label><input id=${t.id} class="quiet" name="name" .value=${t.name} maxlength="80" required autocomplete="off">
        <button type="submit" ?disabled=${!this.model.connected}>${this.t("Rename")}</button><button type="button" class="with-icon" ?disabled=${!this.model.connected} @click=${()=>this.send("open_profile",{profileId:t.id})}>${this.icon("external")}${this.t("Open browser")}</button>
      </form></li>`)}</ul>`:l`<p class="empty-small">${this.t("No browser profiles yet.")}</p>`}
      <p class="hint">${this.t("Profiles separate website sessions. They do not change your IP address.")}</p></section>`}history(){let t=new Intl.DateTimeFormat(this.locale(),{dateStyle:"medium",timeStyle:"short"});return l`<section class="secondary"><h1>${this.t("Search history")}</h1><p class="lede">${this.t("Reopen saved results or run the same queries again.")}</p>
      ${this.model.history.length?l`<ul class="rows">${this.model.history.map(s=>l`<li><button class="history-row" ?disabled=${this.model.running||!this.model.connected} @click=${()=>{this.send("load_search",{id:s.id}),this.tab="search"}}>
        <span class="h-main"><span class="h-queries">${s.request.queries.map(r=>l`<code translate="no">${r}</code>`)}</span><span class="h-meta"><time datetime=${s.created_at}>${t.format(new Date(s.created_at))}</time><span translate="no">${V.filter(([r])=>s.request.engines[r]).map(([,r])=>r).join(" \xB7 ")}</span></span></span>
        <span class="h-count"><strong>${s.count}</strong> ${this.t("results")}</span></button></li>`)}</ul>`:l`<p class="empty-small">${this.t("No saved searches yet")}</p>`}</section>`}render(){let t=document.documentElement.dataset.theme==="dark";return l`<div class="shell"><header><a class="brand" href="#" translate="no" @click=${s=>{s.preventDefault(),this.tab="search"}}><img src=${t?"assets/synthesix-mark-reversed.svg":"assets/synthesix-mark.svg"} alt="" width="22" height="22">Synthesix</a><nav aria-label=${this.t("Navigation")}>${[["search","Search"],["profiles","Browser profiles"],["history","History"]].map(([s,r])=>l`<button aria-current=${this.tab===s?"page":"false"} @click=${()=>{this.tab=s}}>${this.t(r)}</button>`)}</nav><div class="preferences"><label class="sr-only" for="language">${this.t("Language")}</label><select id="language" .value=${window.synthesixI18n?.currentLanguage()??"fr"} @change=${s=>{window.synthesixI18n?.setLanguage(s.target.value),this.requestUpdate()}}><option value="fr">Français</option><option value="en">English</option><option value="es">Español</option><option value="pt">Português</option><option value="de">Deutsch</option><option value="zh">中文</option></select><button class="icon-button" title=${this.t("Toggle theme")} aria-label=${this.t("Toggle theme")} @click=${()=>window.synthesixTheme?.setTheme(t?"light":"dark")}>${this.icon(t?"sun":"moon")}</button></div></header><div class="workspace">${this.composer()}<main>${this.tab==="search"?this.results():this.tab==="profiles"?this.profiles():this.history()}</main></div></div>`}};v.styles=$`
    :host { display:block; color:var(--text); font:14px/1.5 var(--font-body); --rule:color-mix(in srgb, var(--line) 65%, transparent); --control-line:var(--border-strong); }
    * { box-sizing:border-box; } h1,h2,p { margin:0; } button,input,textarea,select { font:inherit; color:inherit; }
    button,input,textarea,select { border:1px solid var(--control-line); border-radius:8px; background:var(--field); }
    button { cursor:pointer; padding:0 14px; min-height:36px; font-weight:500; touch-action:manipulation; transition:background-color .12s, border-color .12s; }
    button:hover:not(:disabled) { background:var(--surface-sunken); } button:active:not(:disabled) { transform:translateY(1px); }
    button:disabled { opacity:.55; cursor:not-allowed; } input,select { min-height:36px; padding:0 10px; min-width:0; }
    input:hover,textarea:hover,select:hover { border-color:var(--muted); }
    input:focus-visible,textarea:focus-visible,select:focus-visible,button:focus-visible,a:focus-visible,summary:focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
    ::placeholder { color:var(--muted); opacity:.8; }
    .icon { flex:none; display:block; }
    .sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }

    /* Framed sheet: one tinted L (header + composer) around the work sheet, inset 8px right and bottom. */
    .shell { min-height:100vh; background:var(--bg-body); }
    header { height:52px; display:flex; align-items:center; gap:28px; padding:0 16px 0 20px; }
    .brand { font:600 18px var(--font-ui); letter-spacing:-.01em; display:flex; gap:9px; align-items:center; color:var(--text); text-decoration:none; border-radius:6px; }
    nav { display:flex; gap:4px; align-self:stretch; }
    nav button { border:0; border-radius:0; background:none; padding:0 10px; border-bottom:2px solid transparent; color:var(--muted); font-weight:500; }
    nav button:hover:not(:disabled) { background:none; color:var(--text); }
    nav button[aria-current=page] { color:var(--text); border-bottom-color:var(--text); }
    .preferences { margin-left:auto; display:flex; gap:6px; } .preferences select { min-height:32px; border-color:transparent; background:transparent; color:var(--muted); }
    .preferences select:hover { border-color:var(--control-line); color:var(--text); }
    .icon-button { min-height:32px; width:32px; padding:0; display:grid; place-items:center; border-color:transparent; background:transparent; color:var(--muted); }
    .icon-button:hover:not(:disabled) { color:var(--text); }
    .workspace { display:grid; grid-template-columns:304px minmax(0,1fr); gap:8px; padding:0 8px 8px 0; min-height:calc(100vh - 52px); }

    /* Composer */
    aside { padding:12px 20px 24px; } aside form { display:flex; flex-direction:column; gap:20px; }
    aside h2 { font:600 16px var(--font-ui); }
    .group { display:flex; flex-direction:column; gap:8px; }
    label { display:flex; flex-direction:column; gap:6px; font-size:13px; font-weight:500; }
    .label-row { display:flex; justify-content:space-between; align-items:baseline; font-size:13px; font-weight:500; }
    .counter { font-size:12px; font-weight:400; color:var(--muted); font-variant-numeric:tabular-nums; } .counter.over { color:var(--danger); font-weight:600; }
    textarea { padding:10px 12px; resize:vertical; width:100%; min-height:132px; line-height:1.65; font:13px/1.65 var(--font-mono); }
    .check { flex-direction:row; align-items:center; gap:8px; font-weight:400; } .check input { min-height:0; width:15px; height:15px; margin:0; accent-color:var(--accent); }
    fieldset { border:0; padding:0; margin:0; min-width:0; } legend { padding:0 0 8px; font-size:13px; font-weight:500; }
    .engine-grid { display:grid; grid-template-columns:1fr 1fr; gap:6px; }
    .engine { flex-direction:row; align-items:center; gap:8px; min-height:36px; padding:0 10px; border:1px solid var(--control-line); border-radius:8px; background:var(--field); color:var(--muted); font-weight:500; cursor:pointer; transition:border-color .12s, color .12s; }
    .engine input { min-height:0; width:15px; height:15px; margin:0; accent-color:var(--accent); }
    .engine:hover { color:var(--text); } .engine:has(input:checked) { color:var(--text); border-color:color-mix(in srgb, var(--accent) 60%, var(--control-line)); }
    .engine:has(input:focus-visible) { outline:2px solid var(--accent); outline-offset:2px; } .engine input:focus-visible { outline:0; }
    details > summary { cursor:pointer; list-style:none; display:flex; align-items:center; gap:8px; font-size:13px; font-weight:600; border-radius:6px; }
    details > summary::-webkit-details-marker { display:none; }
    details > summary::before { content:""; width:6px; height:6px; border:solid currentColor; border-width:0 1.5px 1.5px 0; transform:rotate(-45deg); transition:transform .15s; margin:0 2px 0 1px; opacity:.7; }
    details[open] > summary::before { transform:rotate(45deg); }
    .badge { min-width:20px; height:20px; padding:0 6px; border-radius:999px; display:inline-grid; place-items:center; font-size:12px; background:var(--accent-soft); color:var(--accent-ink); font-variant-numeric:tabular-nums; }
    .fields { display:grid; grid-template-columns:1fr 1fr; gap:12px 8px; padding-top:14px; } .fields label { min-width:0; font-weight:400; }
    .count { flex-direction:row; justify-content:space-between; align-items:center; } .count input { width:72px; text-align:right; font-variant-numeric:tabular-nums; }
    .submit { display:flex; flex-direction:column; gap:8px; padding-top:4px; }
    .plan { font-size:13px; color:var(--muted); font-variant-numeric:tabular-nums; } .plan strong { color:var(--text); font-weight:600; }
    button.primary { color:var(--button-primary-text); background:var(--button-primary-bg); border-color:var(--button-primary-bg); min-height:40px; }
    button.primary:hover:not(:disabled) { background:var(--button-primary-bg); filter:brightness(1.18); }
    .hint { font-size:12px; line-height:1.6; color:var(--muted); }

    /* Sheet */
    main { min-width:0; background:var(--surface); border:1px solid var(--line); border-radius:16px; }
    .results,.secondary { padding:28px 32px 32px; } .secondary { max-width:880px; }
    h1 { font:600 22px/1.25 var(--font-ui); letter-spacing:-.01em; }
    .heading { display:flex; justify-content:space-between; gap:24px; align-items:flex-end; }
    .total { font-weight:400; color:var(--muted); margin-left:4px; font-variant-numeric:tabular-nums; }
    .status { font-size:13px; color:var(--muted); margin-top:6px; min-height:20px; } .status.error { color:var(--danger); }
    .progress { font-variant-numeric:tabular-nums; } .status .progress::before { content:"·"; margin:0 6px; }
    .profile-picker { flex:none; width:240px; font-weight:400; color:var(--muted); font-size:12px; } .profile-picker select { color:var(--text); font-size:14px; }
    progress { display:block; width:100%; height:2px; margin-top:16px; border:0; appearance:none; background:var(--surface-sunken); }
    progress::-webkit-progress-bar { background:var(--surface-sunken); } progress::-webkit-progress-value { background:var(--accent); transition:width .2s; }
    .tools { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin-top:20px; }
    .search-field { position:relative; flex:1 1 240px; max-width:520px; } .search-field .icon { position:absolute; left:11px; top:50%; transform:translateY(-50%); color:var(--muted); pointer-events:none; }
    .search-field input { width:100%; padding-left:34px; }
    .chips { display:flex; gap:4px; padding:3px; border-radius:10px; background:var(--surface-sunken); overflow-x:auto; scrollbar-width:none; }
    .chip { flex:none; display:inline-flex; align-items:center; gap:7px; min-height:30px; padding:0 10px; border:0; border-radius:7px; background:transparent; color:var(--muted); }
    .chip:hover:not(:disabled) { background:transparent; color:var(--text); }
    .chip[aria-pressed=true] { background:var(--field); color:var(--text); box-shadow:0 0 0 1px var(--line); }
    .chip .n { font-size:12px; font-weight:400; font-variant-numeric:tabular-nums; color:var(--muted); }

    .coverage { margin-top:16px; padding:10px 12px; border-radius:10px; background:var(--surface-sunken); }
    .coverage > summary { font-weight:500; } .figure { font-weight:400; color:var(--muted); font-variant-numeric:tabular-nums; }
    .pill { display:inline-flex; align-items:center; height:20px; padding:0 8px; border-radius:999px; font-size:12px; font-weight:500; white-space:nowrap; flex:none; }
    .pill.bad { background:var(--danger-soft); color:var(--danger-ink); }
    .table-wrap { overflow-x:auto; margin-top:10px; }
    table { width:100%; max-width:760px; border-collapse:collapse; font-size:13px; font-variant-numeric:tabular-nums; }
    th,td { padding:7px 0 7px 16px; text-align:left; border-top:1px solid var(--rule); vertical-align:middle; } th:first-child { padding-left:0; }
    thead th { border-top:0; font-weight:400; color:var(--muted); font-size:12px; padding-top:0; }
    tbody th { font-weight:400; max-width:0; width:55%; } .num { text-align:right; white-space:nowrap; } .dim { color:var(--muted); }
    code { font:12px var(--font-mono); } th code { display:block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

    .result-list { margin-top:20px; }
    /* Score column on the left of the title: 48px + 20px gap, text keeps one left edge. */
    .list-head { font-size:12px; color:var(--muted); padding-bottom:8px; white-space:nowrap; }
    article { display:grid; grid-template-columns:48px minmax(0,1fr); column-gap:20px; padding:16px 0 18px; border-top:1px solid var(--rule); }
    article > * { grid-column:2; min-width:0; }
    .where { display:flex; min-width:0; font-size:12.5px; white-space:nowrap; } .host { color:var(--text); font-weight:500; flex:none; max-width:100%; overflow:hidden; text-overflow:ellipsis; }
    .path { color:var(--muted); overflow:hidden; text-overflow:ellipsis; }
    article h2 { margin-top:3px; font:500 17px/1.35 var(--font-ui); max-width:78ch; }
    article a { color:var(--accent-link); text-decoration:none; overflow-wrap:anywhere; border-radius:3px; } article a:hover { text-decoration:underline; text-underline-offset:3px; } article a:visited { color:color-mix(in srgb, var(--accent-link) 70%, var(--text)); }
    .score { grid-column:1; grid-row:2; align-self:baseline; text-align:right; font:500 15px var(--font-ui); color:var(--muted); font-variant-numeric:tabular-nums; }
    .score.strong { color:var(--accent); font-weight:700; }
    .desc { margin-top:6px; max-width:78ch; line-height:1.6; overflow-wrap:anywhere; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }
    .meta { display:flex; flex-wrap:wrap; align-items:center; gap:6px; margin-top:10px; }
    .tag { font-size:12px; font-weight:500; padding:1px 8px; border-radius:5px; background:var(--surface-sunken); color:var(--muted); }
    .via { font-size:12px; color:var(--muted); margin-left:6px; }
    .meta code { padding:1px 6px; border-radius:5px; background:var(--accent-soft); color:var(--accent-ink); overflow-wrap:anywhere; }
    .more { margin-top:16px; }
    .empty { min-height:280px; display:flex; flex-direction:column; justify-content:center; gap:10px; max-width:480px; }
    .empty h2 { font:600 18px var(--font-ui); } .empty p { line-height:1.65; color:var(--muted); }

    /* Profiles and history */
    .lede { margin-top:8px; line-height:1.65; color:var(--muted); max-width:62ch; }
    .inline-form { display:flex; gap:8px; align-items:end; margin:28px 0 0; } .inline-form label { flex:1; max-width:380px; }
    .inline-form button { min-height:36px; }
    .secondary > .status { margin:12px 0 8px; }
    .rows { list-style:none; margin:0; padding:0; } .lede + .rows,.lede + .empty-small { margin-top:24px; }
    .profile-row { display:flex; align-items:center; gap:8px; padding:10px 0; border-top:1px solid var(--rule); }
    .avatar { flex:none; width:32px; height:32px; border-radius:50%; display:grid; place-items:center; font:600 14px var(--font-ui); background:hsl(var(--hue) 42% 88%); color:hsl(var(--hue) 45% 26%); }
    :host-context([data-theme="dark"]) .avatar { background:hsl(var(--hue) 22% 26%); color:hsl(var(--hue) 50% 84%); }
    .quiet { flex:1; border-color:transparent; background:transparent; font-weight:500; } .quiet:hover { border-color:var(--control-line); } .quiet:focus-visible { background:var(--field); }
    .with-icon { display:inline-flex; align-items:center; gap:8px; }
    .empty-small { padding:24px 0; color:var(--muted); border-top:1px solid var(--rule); }
    .secondary > .hint { margin-top:20px; }
    .history-row { display:flex; justify-content:space-between; align-items:center; gap:24px; width:100%; padding:14px 8px; margin:0 -8px; text-align:left; background:none; border:0; border-top:1px solid var(--rule); border-radius:0; font-weight:400; box-sizing:content-box; }
    .history-row:hover:not(:disabled) { background:var(--surface-sunken); }
    .h-main { display:flex; flex-direction:column; gap:6px; min-width:0; } .h-queries { display:flex; flex-wrap:wrap; gap:6px; }
    .h-queries code { padding:2px 7px; border-radius:5px; background:var(--surface-sunken); color:var(--text); overflow-wrap:anywhere; }
    .history-row:hover .h-queries code { background:var(--surface); }
    .h-meta { display:flex; flex-wrap:wrap; gap:4px 12px; font-size:12px; color:var(--muted); }
    .h-count { white-space:nowrap; color:var(--muted); font-variant-numeric:tabular-nums; } .h-count strong { color:var(--text); font-weight:600; }

    @media (prefers-reduced-motion: reduce) { * { transition:none !important; } button:active:not(:disabled) { transform:none; } }
    @media (max-width:1000px) { .workspace { grid-template-columns:272px minmax(0,1fr); } .results,.secondary { padding:24px 20px; } .heading { flex-wrap:wrap; align-items:flex-start; } }
    @media (max-width:680px) {
      header { height:auto; flex-wrap:wrap; gap:4px 12px; padding:10px 12px 0; } .brand { font-size:17px; }
      nav { order:3; width:100%; min-height:42px; } nav button { padding:0 8px; } .preferences select { max-width:110px; }
      .workspace { display:block; padding:0 8px 8px; } aside { padding:16px 8px 24px; } aside form { gap:16px; } textarea { min-height:112px; }
      main { border-radius:12px; } .results,.secondary { padding:20px 14px; } .profile-picker { width:100%; }
      .tools { flex-wrap:wrap; } .search-field { flex-basis:100%; max-width:none; }
      .chips { max-width:100%; } article { grid-template-columns:36px minmax(0,1fr); column-gap:12px; } .score { font-size:14px; }
      .profile-row { flex-wrap:wrap; } .profile-row .quiet { flex-basis:calc(100% - 40px); } .profile-row button { flex:1; justify-content:center; }
      .inline-form { align-items:stretch; flex-direction:column; } .inline-form label { max-width:none; }
      .history-row { flex-direction:column; align-items:flex-start; gap:8px; }
    }
  `,p([b({attribute:!1})],v.prototype,"model",2),p([w()],v.prototype,"queries",2),p([w()],v.prototype,"engines",2),p([w()],v.prototype,"filters",2),p([w()],v.prototype,"automatic",2),p([w()],v.prototype,"count",2),p([w()],v.prototype,"selectedProfile",2),p([w()],v.prototype,"filterText",2),p([w()],v.prototype,"source",2),p([w()],v.prototype,"visible",2),p([w()],v.prototype,"tab",2),p([w()],v.prototype,"profileName",2),v=p([y("sx-browser-app")],v);function qe(){let i=document.querySelector("sx-browser-app");if(!i)return;window.name="synthesix-home";let e=[],t=!1,s=0;window.synthesixHome={setState(r){t=!0,s=Date.now(),i.model={...i.model,...r,connected:!0}},consumeAction(){return e.shift()??null},heartbeat(){return s=Date.now(),t}},setInterval(()=>{s&&Date.now()-s>1e4&&(t=!1,i.model={...i.model,connected:!1,running:!1,status:"Application disconnected. Launch Synthesix to use this page.",isError:!0})},2e3),i.addEventListener("sx-browser-action",r=>{let o=r.detail;typeof window.synthesixDispatch=="function"?window.synthesixDispatch(JSON.stringify(o)):i.model.connected&&e.length<32?e.push(o):window.synthesixHome.setState({status:"Application disconnected. Launch Synthesix to use this page.",isError:!0})})}document.readyState==="loading"?document.addEventListener("DOMContentLoaded",qe,{once:!0}):qe();var P=class extends g{constructor(){super(...arguments);this.accent="none";this.triage=!1}willUpdate(t){t.has("triage")&&(this.triage?(this.setAttribute("data-triage-item",""),this.hasAttribute("tabindex")||this.setAttribute("tabindex","0")):this.removeAttribute("data-triage-item"))}render(){return l`
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
    `}};P.styles=$`
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
  `,p([b({reflect:!0})],P.prototype,"accent",2),p([b({type:Boolean,reflect:!0})],P.prototype,"triage",2),P=p([y("sx-result-card")],P);var M=class extends g{constructor(){super(...arguments);this.level="none";this.tip=!1}updated(t){t.has("tip")&&(this.tabIndex=this.tip?0:-1)}render(){let t=l`<span class="value" part="value"><slot></slot></span>`;return this.tip?l`
      ${t}
      <span class="tooltip" part="tooltip" role="tooltip">
        <slot name="breakdown"></slot>
        <slot name="note"></slot>
      </span>
    `:t}};M.styles=$`
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
  `,p([b({reflect:!0})],M.prototype,"level",2),p([b({type:Boolean,reflect:!0})],M.prototype,"tip",2),M=p([y("sx-score")],M);var E=class extends g{constructor(){super(...arguments);this.tone="muted";this.removable=!1;this.removeLabel="Remove"}_remove(){this.dispatchEvent(new CustomEvent("sx-tag-remove",{bubbles:!0,composed:!0}))}render(){return l`<span class="tag" part="tag">
      <slot></slot>
      ${this.removable?l`<button
            class="remove"
            part="remove"
            type="button"
            aria-label=${this.removeLabel}
            @click=${this._remove}
          >
            &times;
          </button>`:null}
    </span>`}};E.styles=$`
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
  `,p([b({reflect:!0})],E.prototype,"tone",2),p([b({type:Boolean,reflect:!0})],E.prototype,"removable",2),p([b({attribute:"remove-label"})],E.prototype,"removeLabel",2),E=p([y("sx-tag")],E);var W=class extends g{render(){return l`<span class="provenance" part="provenance">
      <slot name="icon"></slot>
      <span class="label" part="label"><slot name="label"></slot></span>
      <span class="detail" part="detail"><slot></slot></span>
    </span>`}};W.styles=$`
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
  `,W=p([y("sx-provenance")],W);})();
