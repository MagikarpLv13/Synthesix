"use strict";(()=>{var Se=Object.defineProperty;var Ce=Object.getOwnPropertyDescriptor;var p=(r,e,t,s)=>{for(var i=s>1?void 0:s?Ce(e,t):e,n=r.length-1,o;n>=0;n--)(o=r[n])&&(i=(s?o(e,t,i):o(i))||i);return s&&i&&Se(e,t,i),i};var F=globalThis,W=F.ShadowRoot&&(F.ShadyCSS===void 0||F.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Q=Symbol(),ce=new WeakMap,H=class{constructor(e,t,s){if(this._$cssResult$=!0,s!==Q)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(W&&e===void 0){let s=t!==void 0&&t.length===1;s&&(e=ce.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),s&&ce.set(t,e))}return e}toString(){return this.cssText}},pe=r=>new H(typeof r=="string"?r:r+"",void 0,Q),b=(r,...e)=>{let t=r.length===1?r[0]:e.reduce((s,i,n)=>s+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+r[n+1],r[0]);return new H(t,r,Q)},de=(r,e)=>{if(W)r.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let s=document.createElement("style"),i=F.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=t.cssText,r.appendChild(s)}},Z=W?r=>r:r=>r instanceof CSSStyleSheet?(e=>{let t="";for(let s of e.cssRules)t+=s.cssText;return pe(t)})(r):r;var{is:Pe,defineProperty:Te,getOwnPropertyDescriptor:Le,getOwnPropertyNames:Me,getOwnPropertySymbols:qe,getPrototypeOf:Re}=Object,G=globalThis,he=G.trustedTypes,He=he?he.emptyScript:"",Oe=G.reactiveElementPolyfillSupport,O=(r,e)=>r,U={toAttribute(r,e){switch(e){case Boolean:r=r?He:null;break;case Object:case Array:r=r==null?r:JSON.stringify(r)}return r},fromAttribute(r,e){let t=r;switch(e){case Boolean:t=r!==null;break;case Number:t=r===null?null:Number(r);break;case Object:case Array:try{t=JSON.parse(r)}catch{t=null}}return t}},K=(r,e)=>!Pe(r,e),ue={attribute:!0,type:String,converter:U,reflect:!1,useDefault:!1,hasChanged:K};Symbol.metadata??=Symbol("metadata"),G.litPropertyMetadata??=new WeakMap;var w=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=ue){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(e,s,t);i!==void 0&&Te(this.prototype,e,i)}}static getPropertyDescriptor(e,t,s){let{get:i,set:n}=Le(this.prototype,e)??{get(){return this[t]},set(o){this[t]=o}};return{get:i,set(o){let c=i?.call(this);n?.call(this,o),this.requestUpdate(e,c,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??ue}static _$Ei(){if(this.hasOwnProperty(O("elementProperties")))return;let e=Re(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(O("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(O("properties"))){let t=this.properties,s=[...Me(t),...qe(t)];for(let i of s)this.createProperty(i,t[i])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[s,i]of t)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[t,s]of this.elementProperties){let i=this._$Eu(t,s);i!==void 0&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let s=new Set(e.flat(1/0).reverse());for(let i of s)t.unshift(Z(i))}else e!==void 0&&t.push(Z(e));return t}static _$Eu(e,t){let s=t.attribute;return s===!1?void 0:typeof s=="string"?s:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let s of t.keys())this.hasOwnProperty(s)&&(e.set(s,this[s]),delete this[s]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return de(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,s){this._$AK(e,s)}_$ET(e,t){let s=this.constructor.elementProperties.get(e),i=this.constructor._$Eu(e,s);if(i!==void 0&&s.reflect===!0){let n=(s.converter?.toAttribute!==void 0?s.converter:U).toAttribute(t,s.type);this._$Em=e,n==null?this.removeAttribute(i):this.setAttribute(i,n),this._$Em=null}}_$AK(e,t){let s=this.constructor,i=s._$Eh.get(e);if(i!==void 0&&this._$Em!==i){let n=s.getPropertyOptions(i),o=typeof n.converter=="function"?{fromAttribute:n.converter}:n.converter?.fromAttribute!==void 0?n.converter:U;this._$Em=i;let c=o.fromAttribute(t,n.type);this[i]=c??this._$Ej?.get(i)??c,this._$Em=null}}requestUpdate(e,t,s,i=!1,n){if(e!==void 0){let o=this.constructor;if(i===!1&&(n=this[e]),s??=o.getPropertyOptions(e),!((s.hasChanged??K)(n,t)||s.useDefault&&s.reflect&&n===this._$Ej?.get(e)&&!this.hasAttribute(o._$Eu(e,s))))return;this.C(e,t,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:s,reflect:i,wrapped:n},o){s&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,o??t??this[e]),n!==!0||o!==void 0)||(this._$AL.has(e)||(this.hasUpdated||s||(t=void 0),this._$AL.set(e,t)),i===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,n]of this._$Ep)this[i]=n;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,n]of s){let{wrapped:o}=n,c=this[i];o!==!0||this._$AL.has(i)||c===void 0||this.C(i,void 0,n,c)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(t)):this._$EM()}catch(s){throw e=!1,this._$EM(),s}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};w.elementStyles=[],w.shadowRootOptions={mode:"open"},w[O("elementProperties")]=new Map,w[O("finalized")]=new Map,Oe?.({ReactiveElement:w}),(G.reactiveElementVersions??=[]).push("2.1.2");var oe=globalThis,me=r=>r,J=oe.trustedTypes,fe=J?J.createPolicy("lit-html",{createHTML:r=>r}):void 0,ye="$lit$",E=`lit$${Math.random().toFixed(9).slice(2)}$`,we="?"+E,Ue=`<${we}>`,C=document,D=()=>C.createComment(""),z=r=>r===null||typeof r!="object"&&typeof r!="function",ne=Array.isArray,Ne=r=>ne(r)||typeof r?.[Symbol.iterator]=="function",X=`[ 	
\f\r]`,N=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ge=/-->/g,ve=/>/g,k=RegExp(`>|${X}(?:([^\\s"'>=/]+)(${X}*=${X}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),be=/'/g,xe=/"/g,_e=/^(?:script|style|textarea|title)$/i,ae=r=>(e,...t)=>({_$litType$:r,strings:e,values:t}),l=ae(1),Je=ae(2),Ye=ae(3),P=Symbol.for("lit-noChange"),u=Symbol.for("lit-nothing"),$e=new WeakMap,S=C.createTreeWalker(C,129);function Ee(r,e){if(!ne(r)||!r.hasOwnProperty("raw"))throw Error("invalid template strings array");return fe!==void 0?fe.createHTML(e):e}var De=(r,e)=>{let t=r.length-1,s=[],i,n=e===2?"<svg>":e===3?"<math>":"",o=N;for(let c=0;c<t;c++){let a=r[c],h,g,d=-1,y=0;for(;y<a.length&&(o.lastIndex=y,g=o.exec(a),g!==null);)y=o.lastIndex,o===N?g[1]==="!--"?o=ge:g[1]!==void 0?o=ve:g[2]!==void 0?(_e.test(g[2])&&(i=RegExp("</"+g[2],"g")),o=k):g[3]!==void 0&&(o=k):o===k?g[0]===">"?(o=i??N,d=-1):g[1]===void 0?d=-2:(d=o.lastIndex-g[2].length,h=g[1],o=g[3]===void 0?k:g[3]==='"'?xe:be):o===xe||o===be?o=k:o===ge||o===ve?o=N:(o=k,i=void 0);let _=o===k&&r[c+1].startsWith("/>")?" ":"";n+=o===N?a+Ue:d>=0?(s.push(h),a.slice(0,d)+ye+a.slice(d)+E+_):a+E+(d===-2?c:_)}return[Ee(r,n+(r[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),s]},j=class r{constructor({strings:e,_$litType$:t},s){let i;this.parts=[];let n=0,o=0,c=e.length-1,a=this.parts,[h,g]=De(e,t);if(this.el=r.createElement(h,s),S.currentNode=this.el.content,t===2||t===3){let d=this.el.content.firstChild;d.replaceWith(...d.childNodes)}for(;(i=S.nextNode())!==null&&a.length<c;){if(i.nodeType===1){if(i.hasAttributes())for(let d of i.getAttributeNames())if(d.endsWith(ye)){let y=g[o++],_=i.getAttribute(d).split(E),V=/([.?@])?(.*)/.exec(y);a.push({type:1,index:n,name:V[2],strings:_,ctor:V[1]==="."?te:V[1]==="?"?se:V[1]==="@"?ie:q}),i.removeAttribute(d)}else d.startsWith(E)&&(a.push({type:6,index:n}),i.removeAttribute(d));if(_e.test(i.tagName)){let d=i.textContent.split(E),y=d.length-1;if(y>0){i.textContent=J?J.emptyScript:"";for(let _=0;_<y;_++)i.append(d[_],D()),S.nextNode(),a.push({type:2,index:++n});i.append(d[y],D())}}}else if(i.nodeType===8)if(i.data===we)a.push({type:2,index:n});else{let d=-1;for(;(d=i.data.indexOf(E,d+1))!==-1;)a.push({type:7,index:n}),d+=E.length-1}n++}}static createElement(e,t){let s=C.createElement("template");return s.innerHTML=e,s}};function M(r,e,t=r,s){if(e===P)return e;let i=s!==void 0?t._$Co?.[s]:t._$Cl,n=z(e)?void 0:e._$litDirective$;return i?.constructor!==n&&(i?._$AO?.(!1),n===void 0?i=void 0:(i=new n(r),i._$AT(r,t,s)),s!==void 0?(t._$Co??=[])[s]=i:t._$Cl=i),i!==void 0&&(e=M(r,i._$AS(r,e.values),i,s)),e}var ee=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:s}=this._$AD,i=(e?.creationScope??C).importNode(t,!0);S.currentNode=i;let n=S.nextNode(),o=0,c=0,a=s[0];for(;a!==void 0;){if(o===a.index){let h;a.type===2?h=new I(n,n.nextSibling,this,e):a.type===1?h=new a.ctor(n,a.name,a.strings,this,e):a.type===6&&(h=new re(n,this,e)),this._$AV.push(h),a=s[++c]}o!==a?.index&&(n=S.nextNode(),o++)}return S.currentNode=C,i}p(e){let t=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(e,s,t),t+=s.strings.length-2):s._$AI(e[t])),t++}},I=class r{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,s,i){this.type=2,this._$AH=u,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=M(this,e,t),z(e)?e===u||e==null||e===""?(this._$AH!==u&&this._$AR(),this._$AH=u):e!==this._$AH&&e!==P&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Ne(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==u&&z(this._$AH)?this._$AA.nextSibling.data=e:this.T(C.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:s}=e,i=typeof s=="number"?this._$AC(e):(s.el===void 0&&(s.el=j.createElement(Ee(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(t);else{let n=new ee(i,this),o=n.u(this.options);n.p(t),this.T(o),this._$AH=n}}_$AC(e){let t=$e.get(e.strings);return t===void 0&&$e.set(e.strings,t=new j(e)),t}k(e){ne(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,s,i=0;for(let n of e)i===t.length?t.push(s=new r(this.O(D()),this.O(D()),this,this.options)):s=t[i],s._$AI(n),i++;i<t.length&&(this._$AR(s&&s._$AB.nextSibling,i),t.length=i)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let s=me(e).nextSibling;me(e).remove(),e=s}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},q=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,s,i,n){this.type=1,this._$AH=u,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=n,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=u}_$AI(e,t=this,s,i){let n=this.strings,o=!1;if(n===void 0)e=M(this,e,t,0),o=!z(e)||e!==this._$AH&&e!==P,o&&(this._$AH=e);else{let c=e,a,h;for(e=n[0],a=0;a<n.length-1;a++)h=M(this,c[s+a],t,a),h===P&&(h=this._$AH[a]),o||=!z(h)||h!==this._$AH[a],h===u?e=u:e!==u&&(e+=(h??"")+n[a+1]),this._$AH[a]=h}o&&!i&&this.j(e)}j(e){e===u?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},te=class extends q{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===u?void 0:e}},se=class extends q{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==u)}},ie=class extends q{constructor(e,t,s,i,n){super(e,t,s,i,n),this.type=5}_$AI(e,t=this){if((e=M(this,e,t,0)??u)===P)return;let s=this._$AH,i=e===u&&s!==u||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,n=e!==u&&(s===u||i);i&&this.element.removeEventListener(this.name,this,s),n&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},re=class{constructor(e,t,s){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(e){M(this,e)}};var ze=oe.litHtmlPolyfillSupport;ze?.(j,I),(oe.litHtmlVersions??=[]).push("3.3.3");var Ae=(r,e,t)=>{let s=t?.renderBefore??e,i=s._$litPart$;if(i===void 0){let n=t?.renderBefore??null;s._$litPart$=i=new I(e.insertBefore(D(),n),n,void 0,t??{})}return i._$AI(r),i};var le=globalThis,m=class extends w{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Ae(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return P}};m._$litElement$=!0,m.finalized=!0,le.litElementHydrateSupport?.({LitElement:m});var je=le.litElementPolyfillSupport;je?.({LitElement:m});(le.litElementVersions??=[]).push("4.2.2");var x=r=>(e,t)=>{t!==void 0?t.addInitializer(()=>{customElements.define(r,e)}):customElements.define(r,e)};var Ie={attribute:!0,type:String,converter:U,reflect:!1,hasChanged:K},Be=(r=Ie,e,t)=>{let{kind:s,metadata:i}=t,n=globalThis.litPropertyMetadata.get(i);if(n===void 0&&globalThis.litPropertyMetadata.set(i,n=new Map),s==="setter"&&((r=Object.create(r)).wrapped=!0),n.set(t.name,r),s==="accessor"){let{name:o}=t;return{set(c){let a=e.get.call(this);e.set.call(this,c),this.requestUpdate(o,a,r,!0,c)},init(c){return c!==void 0&&this.C(o,void 0,r,c),c}}}if(s==="setter"){let{name:o}=t;return function(c){let a=this[o];e.call(this,c),this.requestUpdate(o,a,r,!0,c)}}throw Error("Unsupported decorator location: "+s)};function v(r){return(e,t)=>typeof t=="object"?Be(r,e,t):((s,i,n)=>{let o=i.hasOwnProperty(n);return i.constructor.createProperty(n,s),o?Object.getOwnPropertyDescriptor(i,n):void 0})(r,e,t)}function $(r){return v({...r,state:!0,attribute:!1})}var R=class extends m{constructor(){super(...arguments);this.tone="neutral"}render(){return l`<span class="chip"><slot></slot></span>`}};R.styles=b`
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
  `,p([v({reflect:!0})],R.prototype,"tone",2),R=p([x("sx-chip")],R);var f=class extends m{constructor(){super(...arguments);this.model={connected:!1,running:!1,results:[],profiles:[],history:[],coverage:[],status:"Starting Synthesix...",isError:!1};this.queries="";this.engines={google:!0,bing:!0,brave:!0,duckduckgo:!0};this.filters={};this.automatic=!0;this.count=20;this.selectedProfile="";this.filterText="";this.source="";this.visible=100;this.tab="search";this.profileName="";this.observer=new MutationObserver(()=>this.requestUpdate())}connectedCallback(){super.connectedCallback(),this.observer.observe(document.documentElement,{attributes:!0,attributeFilter:["lang","data-theme"]})}disconnectedCallback(){this.observer.disconnect(),super.disconnectedCallback()}updated(t){let s=t.get("model");if(t.has("model")&&this.model.request&&this.model.request!==s?.request){let i=this.model.request;this.queries=i.queries.join(`
`),this.engines={...i.engines},this.filters={...i.filters},this.automatic=i.automaticDorks,this.count=i.numResults,this.tab="search"}}t(t){return window.synthesixI18n?.t(t)??t}send(t,s={}){this.dispatchEvent(new CustomEvent("sx-browser-action",{detail:{action:t,...s},bubbles:!0,composed:!0}))}search(t){t.preventDefault(),this.visible=100,this.filterText="",this.source="",this.send("search",{queries:this.queries.split(`
`).map(s=>s.trim()).filter(Boolean),engines:this.engines,filters:this.filters,numResults:this.count,automaticDorks:this.automatic})}field(t,s,i="text"){return l`<label>${this.t(s)}<input type=${i} name=${t} maxlength="500" .value=${this.filters[t]??""} @input=${n=>{this.filters={...this.filters,[t]:n.target.value}}}></label>`}safeUrl(t){try{let s=new URL(t);return["http:","https:"].includes(s.protocol)&&!s.username&&!s.password?s.href:""}catch{return""}}open(t,s){t.preventDefault(),this.safeUrl(s.link)&&this.send("open_result",{url:s.link,profileId:this.selectedProfile})}profileSelect(){return l`<label class="profile-picker">${this.t("Open results with")}<select aria-label=${this.t("Open results with")} .value=${this.selectedProfile} @change=${t=>{this.selectedProfile=t.target.value}}><option value="">${this.t("Neutral profile")}</option>${this.model.profiles.map(t=>l`<option value=${t.id}>${t.name}</option>`)}</select></label>`}composer(){return l`<aside><form @submit=${this.search}>
      <h2>${this.t("Build your search")}</h2>
      <label for="queries">${this.t("Queries")}</label>
      <textarea id="queries" name="queries" rows="6" required maxlength="10020" spellcheck="false" .value=${this.queries} @input=${t=>{this.queries=t.target.value}} placeholder=${this.t("One query per line")}></textarea>
      <label class="check"><input type="checkbox" .checked=${this.automatic} @change=${t=>{this.automatic=t.target.checked}}>${this.t("Automatic exact-phrase dorks")}</label>
      <fieldset><legend>${this.t("Search engines")}</legend><div class="engine-grid">${[["google","Google"],["bing","Bing"],["brave","Brave"],["duckduckgo","DuckDuckGo"]].map(([t,s])=>l`<label class="check"><input type="checkbox" name=${t} .checked=${!!this.engines[t]} @change=${i=>{this.engines={...this.engines,[t]:i.target.checked}}}>${s}</label>`)}</div></fieldset>
      <details><summary>${this.t("Dork filters")}</summary><div class="fields">${this.field("site","Site")}${this.field("exclude","Exclude")}${this.field("filetype","File type")}${this.field("title","Title contains")}${this.field("url","URL contains")}${this.field("body","Page contains")}${this.field("country","Country code")}${this.field("after","After","date")}${this.field("before","Before","date")}</div></details>
      <label class="count">${this.t("Results per engine")}<input type="number" min="1" max="100" .value=${String(this.count)} @change=${t=>{this.count=Number(t.target.value)}}></label>
      <button class="primary" type="submit" ?disabled=${!this.model.connected||this.model.running}>${this.t("Search")}</button>
      ${this.model.running?l`<button type="button" @click=${()=>this.send("cancel_search")}>${this.t("Cancel search")}</button>`:""}
      <p class="muted hint">${this.t("Queries are merged into one deduplicated result list.")}</p>
    </form></aside>`}results(){let t=this.filterText.toLocaleLowerCase(),s=this.model.results.filter(o=>(!this.source||o.source.toLowerCase().includes(this.source))&&`${o.title} ${o.description??""} ${o.link}`.toLocaleLowerCase().includes(t)),i=this.model.coverage.reduce((o,c)=>o+Object.keys(c.engines).length,0),n=this.model.coverage.length*Object.values(this.model.request?.engines??this.engines).filter(Boolean).length;return l`<section class="results" aria-busy=${String(this.model.running)}><div class="heading"><div><h1>${this.t("Search results")} <span class="total">${s.length}</span></h1>${n?l`<p class="muted progress">${i} / ${n} ${this.t("engine requests completed")}</p>`:""}</div>${this.profileSelect()}</div>
      <div class="tools"><input aria-label=${this.t("Filter results")} placeholder=${this.t("Filter results")} type="search" .value=${this.filterText} @input=${o=>{this.filterText=o.target.value,this.visible=100}}><select aria-label=${this.t("Search engines")} .value=${this.source} @change=${o=>{this.source=o.target.value}}><option value="">${this.t("All engines")}</option>${["Google","Bing","Brave","DuckDuckGo"].map(o=>l`<option value=${o.toLowerCase()}>${o}</option>`)}</select></div>
      <p class=${this.model.isError?"status error":"status"} role="status" aria-live="polite">${this.t(this.model.status)}</p>
      ${this.model.coverage.some(o=>Object.values(o.engines).some(c=>c.status!=="ok"))?l`<details class="coverage"><summary>${this.t("Search coverage")}</summary>${this.model.coverage.map(o=>l`<div class="coverage-row"><code>${o.query}</code><span>${Object.entries(o.engines).map(([c,a])=>l`<span class=${a.status==="ok"?"":"error"}>${c}: ${this.t(a.status)} (${a.count}) </span>`)}</span></div>`)}</details>`:""}
      ${s.length?l`<div class="result-list">${s.slice(0,this.visible).map(o=>l`<article><div class="result-source"><span>${o.source}</span>${o.relevance_score!=null?l`<span title=${this.t("Relevance")}>${o.relevance_score.toFixed(1)}</span>`:""}</div><h2><a href=${this.safeUrl(o.link)||void 0} @click=${c=>this.open(c,o)}>${o.title||o.link}</a></h2><div class="url">${o.link}</div>${o.description?l`<p>${o.description}</p>`:""}${o.query_variants?.length?l`<div class="found-via">${this.t("Found via")} ${o.query_variants.join(" \xB7 ")}</div>`:""}</article>`)}</div>${s.length>this.visible?l`<button class="more" @click=${()=>{this.visible+=100}}>${this.t("Show more results")}</button>`:""}`:l`<div class="empty"><h2>${this.t(this.model.results.length?"No results match this filter.":this.model.running?"Searching selected engines...":"Your next search starts here.")}</h2><p>${this.t("Write your queries on the left, choose your engines, then search.")}</p></div>`}
    </section>`}profiles(){return l`<section class="secondary"><h1>${this.t("Browser profiles")}</h1><p class="muted">${this.t("Each profile keeps its own website logins. Sign in once in its browser window.")}</p><form class="inline-form" @submit=${t=>{t.preventDefault(),this.send("create_profile",{name:this.profileName}),this.profileName=""}}><label>${this.t("Profile name")}<input required maxlength="80" .value=${this.profileName} @input=${t=>{this.profileName=t.target.value}}></label><button class="primary" ?disabled=${!this.model.connected}>${this.t("Create profile")}</button></form><p class="status" role="status">${this.t(this.model.status)}</p>
      ${this.model.profiles.map(t=>l`<form class="profile-row" @submit=${s=>{s.preventDefault();let i=new FormData(s.target);this.send("rename_profile",{profileId:t.id,name:i.get("name")})}}><label class="sr-only" for=${t.id}>${this.t("Profile name")}</label><input id=${t.id} name="name" .value=${t.name} maxlength="80" required><button type="submit" ?disabled=${!this.model.connected}>${this.t("Rename")}</button><button type="button" ?disabled=${!this.model.connected} @click=${()=>this.send("open_profile",{profileId:t.id})}>${this.t("Open browser")}</button></form>`)}
      ${this.model.profiles.length?"":l`<p class="empty-small">${this.t("No browser profiles yet.")}</p>`}<p class="muted hint">${this.t("Profiles separate website sessions. They do not change your IP address.")}</p></section>`}history(){return l`<section class="secondary"><h1>${this.t("Search history")}</h1><p class="muted">${this.t("Reopen saved results or run the same queries again.")}</p>${this.model.history.length?this.model.history.map(t=>l`<button class="history-row" ?disabled=${this.model.running||!this.model.connected} @click=${()=>{this.send("load_search",{id:t.id}),this.tab="search"}}><span><strong>${t.request.queries.join(" \xB7 ")}</strong><time>${new Date(t.created_at).toLocaleString(document.documentElement.lang)}</time></span><span>${t.count} ${this.t("results")}</span></button>`):l`<p class="empty-small">${this.t("No saved searches yet")}</p>`}</section>`}render(){return l`<div class="shell"><header><a class="brand" href="#" @click=${t=>{t.preventDefault(),this.tab="search"}}><img src=${document.documentElement.dataset.theme==="dark"?"assets/synthesix-mark-reversed.svg":"assets/synthesix-mark.svg"} alt="" width="25" height="25">Synthesix</a><nav aria-label=${this.t("Navigation")}>${[["search","Search"],["profiles","Browser profiles"],["history","History"]].map(([t,s])=>l`<button aria-current=${this.tab===t?"page":"false"} @click=${()=>{this.tab=t}}>${this.t(s)}</button>`)}</nav><div class="preferences"><label class="sr-only" for="language">${this.t("Language")}</label><select id="language" .value=${window.synthesixI18n?.currentLanguage()??"fr"} @change=${t=>{window.synthesixI18n?.setLanguage(t.target.value),this.requestUpdate()}}><option value="fr">Français</option><option value="en">English</option><option value="es">Español</option><option value="pt">Português</option><option value="de">Deutsch</option><option value="zh">中文</option></select><button title=${this.t("Toggle theme")} aria-label=${this.t("Toggle theme")} @click=${()=>window.synthesixTheme?.setTheme(document.documentElement.dataset.theme==="dark"?"light":"dark")}>◐</button></div></header><div class="workspace">${this.composer()}<main>${this.tab==="search"?this.results():this.tab==="profiles"?this.profiles():this.history()}</main></div></div>`}};f.styles=b`
    :host { display:block; color:var(--text); font:14px var(--font-body); }
    * { box-sizing:border-box; } button,input,textarea,select { font:inherit; color:inherit; }
    button,input,textarea,select { border:1px solid var(--line); border-radius:6px; background:var(--field); }
    button { cursor:pointer; padding:8px 12px; min-height:36px; } button:hover:not(:disabled) { background:var(--surface-sunken); }
    button:disabled { opacity:.5; cursor:default; } input,select { min-height:36px; padding:7px 9px; min-width:0; }
    input:focus-visible,textarea:focus-visible,select:focus-visible,button:focus-visible,a:focus-visible,summary:focus-visible { outline:2px solid var(--accent); outline-offset:3px; }
    .shell { min-height:100vh; background:var(--bg-body); } header { min-height:56px; display:flex; align-items:center; gap:24px; padding:0 20px; }
    .brand { font:600 20px var(--font-ui); display:flex; gap:9px; align-items:center; color:var(--text); text-decoration:none; } nav { display:flex; gap:8px; align-self:stretch; }
    nav button { border:0; border-radius:0; background:none; padding:0 10px; border-bottom:2px solid transparent; color:var(--muted); } nav button[aria-current=page] { color:var(--text); border-bottom-color:var(--accent); }
    .preferences { margin-left:auto; display:flex; gap:8px; } .preferences button { font-size:20px; padding:2px 10px; }
    /* 304px composer + flexible sheet; 8px outer inset, no unused right column. */
    .workspace { display:grid; grid-template-columns:304px minmax(0,1fr); gap:8px; padding:0 8px 8px 0; min-height:calc(100vh - 56px); }
    aside { padding:20px; } aside form { display:flex; flex-direction:column; gap:16px; } h1,h2,p { margin:0; } h1 { font:600 24px var(--font-ui); } h2 { font:600 16px var(--font-ui); } aside h2 { margin-bottom:4px; }
    label { display:flex; flex-direction:column; gap:7px; font-size:13px; } textarea { padding:10px; resize:vertical; width:100%; min-height:130px; line-height:1.6; font-family:var(--font-mono); }
    .check { display:flex; flex-direction:row; align-items:center; gap:8px; line-height:1.5; } .check input { min-height:0; width:15px; height:15px; margin:0; accent-color:var(--accent); }
    fieldset { border:0; padding:0; margin:0; } legend { padding:0 0 12px; font-size:13px; } .engine-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px 4px; }
    summary { cursor:pointer; font-weight:600; padding:4px 0; } .fields { display:grid; grid-template-columns:1fr 1fr; gap:12px 8px; padding-top:14px; } .fields label { min-width:0; }
    .count { flex-direction:row; justify-content:space-between; align-items:center; } .count input { width:70px; }
    button.primary { color:var(--button-primary-text); background:var(--button-primary-bg); border-color:var(--button-primary-bg); } button.primary:hover:not(:disabled) { filter:brightness(.9); }
    main { min-width:0; background:var(--surface); border:1px solid var(--line); border-radius:16px; } .results,.secondary { padding:24px 28px; } .secondary { max-width:960px; }
    .heading { display:flex; justify-content:space-between; gap:20px; align-items:flex-start; } .total { font-variant-numeric:tabular-nums; font-weight:400; color:var(--muted); margin-left:6px; }
    .profile-picker { max-width:250px; min-width:160px; } .muted,.hint,.url,.found-via { color:var(--muted); } .hint { font-size:12px; line-height:1.65; } .progress { font-size:12px; margin-top:6px; }
    .tools { display:flex; gap:8px; margin-top:22px; } .tools input { flex:1; max-width:600px; } .tools select { max-width:170px; }
    .status { min-height:20px; font-size:13px; margin:16px 0; } .error { color:var(--danger); } .empty { min-height:220px; display:flex; flex-direction:column; justify-content:center; gap:12px; max-width:500px; } .empty p { line-height:1.7; color:var(--muted); }
    .result-list { max-width:900px; } article { padding:18px 0; border-top:1px solid var(--line); } .result-source { display:flex; justify-content:space-between; font-size:12px; color:var(--muted); font-variant-numeric:tabular-nums; }
    article h2 { margin:6px 0; font-size:18px; font-weight:500; } article a { color:var(--accent-link); overflow-wrap:anywhere; text-decoration:none; } article a:hover { text-decoration:underline; } article p { line-height:1.7; margin-top:7px; overflow-wrap:anywhere; }
    .url { font-size:12px; overflow-wrap:anywhere; line-height:1.5; } .found-via { margin-top:8px; font:11px var(--font-mono); overflow-wrap:anywhere; } .more { margin-top:16px; }
    .coverage { font-size:12px; margin-bottom:18px; } .coverage-row { display:flex; flex-wrap:wrap; gap:10px; padding:6px 0; } code { overflow-wrap:anywhere; }
    .secondary > .muted { margin-top:12px; line-height:1.7; } .inline-form { display:flex; gap:12px; align-items:end; margin:24px 0; } .inline-form label { flex:1; max-width:400px; } .profile-row { display:flex; gap:8px; padding:14px 0; border-top:1px solid var(--line); } .profile-row input { flex:1; }
    .empty-small { padding:24px 0; color:var(--muted); } .history-row { display:flex; justify-content:space-between; gap:24px; padding:18px 0; text-align:left; background:none; border:0; border-bottom:1px solid var(--line); border-radius:0; width:100%; }
    .history-row span:first-child { display:flex; flex-direction:column; gap:8px; min-width:0; } .history-row strong { overflow-wrap:anywhere; font-weight:500; } time { font-size:12px; color:var(--muted); } .history-row > span:last-child { white-space:nowrap; font-variant-numeric:tabular-nums; }
    .sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
    @media(max-width:1000px) { .workspace { grid-template-columns:270px minmax(0,1fr); } .results,.secondary { padding:22px 20px; } .heading { flex-wrap:wrap; } }
    @media(max-width:680px) { header { flex-wrap:wrap; gap:8px 12px; padding:12px; } .brand { font-size:18px; } nav { order:3; width:100%; min-height:38px; } nav button { padding:6px 8px; } .preferences { gap:4px; } .preferences select { width:90px; } .workspace { display:block; padding:0 8px 8px; } aside { padding:12px 8px 20px; } aside form { gap:12px; } textarea { min-height:110px; } main { border-radius:10px; } .results,.secondary { padding:20px 14px; } .tools { flex-wrap:wrap; } .tools input { width:100%; min-width:140px; } .profile-row { flex-wrap:wrap; } .profile-row input { flex-basis:100%; } .inline-form { align-items:stretch; flex-direction:column; } }
  `,p([v({attribute:!1})],f.prototype,"model",2),p([$()],f.prototype,"queries",2),p([$()],f.prototype,"engines",2),p([$()],f.prototype,"filters",2),p([$()],f.prototype,"automatic",2),p([$()],f.prototype,"count",2),p([$()],f.prototype,"selectedProfile",2),p([$()],f.prototype,"filterText",2),p([$()],f.prototype,"source",2),p([$()],f.prototype,"visible",2),p([$()],f.prototype,"tab",2),p([$()],f.prototype,"profileName",2),f=p([x("sx-browser-app")],f);function ke(){let r=document.querySelector("sx-browser-app");if(!r)return;window.name="synthesix-home";let e=[],t=!1,s=0;window.synthesixHome={setState(i){t=!0,s=Date.now(),r.model={...r.model,...i,connected:!0}},consumeAction(){return e.shift()??null},heartbeat(){return s=Date.now(),t}},setInterval(()=>{s&&Date.now()-s>1e4&&(t=!1,r.model={...r.model,connected:!1,running:!1,status:"Application disconnected. Launch Synthesix to use this page.",isError:!0})},2e3),r.addEventListener("sx-browser-action",i=>{let n=i.detail;typeof window.synthesixDispatch=="function"?window.synthesixDispatch(JSON.stringify(n)):r.model.connected&&e.length<32?e.push(n):window.synthesixHome.setState({status:"Application disconnected. Launch Synthesix to use this page.",isError:!0})})}document.readyState==="loading"?document.addEventListener("DOMContentLoaded",ke,{once:!0}):ke();var T=class extends m{constructor(){super(...arguments);this.accent="none";this.triage=!1}willUpdate(t){t.has("triage")&&(this.triage?(this.setAttribute("data-triage-item",""),this.hasAttribute("tabindex")||this.setAttribute("tabindex","0")):this.removeAttribute("data-triage-item"))}render(){return l`
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
    `}};T.styles=b`
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
  `,p([v({reflect:!0})],T.prototype,"accent",2),p([v({type:Boolean,reflect:!0})],T.prototype,"triage",2),T=p([x("sx-result-card")],T);var L=class extends m{constructor(){super(...arguments);this.level="none";this.tip=!1}updated(t){t.has("tip")&&(this.tabIndex=this.tip?0:-1)}render(){let t=l`<span class="value" part="value"><slot></slot></span>`;return this.tip?l`
      ${t}
      <span class="tooltip" part="tooltip" role="tooltip">
        <slot name="breakdown"></slot>
        <slot name="note"></slot>
      </span>
    `:t}};L.styles=b`
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
  `,p([v({reflect:!0})],L.prototype,"level",2),p([v({type:Boolean,reflect:!0})],L.prototype,"tip",2),L=p([x("sx-score")],L);var A=class extends m{constructor(){super(...arguments);this.tone="muted";this.removable=!1;this.removeLabel="Remove"}_remove(){this.dispatchEvent(new CustomEvent("sx-tag-remove",{bubbles:!0,composed:!0}))}render(){return l`<span class="tag" part="tag">
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
    </span>`}};A.styles=b`
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
  `,p([v({reflect:!0})],A.prototype,"tone",2),p([v({type:Boolean,reflect:!0})],A.prototype,"removable",2),p([v({attribute:"remove-label"})],A.prototype,"removeLabel",2),A=p([x("sx-tag")],A);var B=class extends m{render(){return l`<span class="provenance" part="provenance">
      <slot name="icon"></slot>
      <span class="label" part="label"><slot name="label"></slot></span>
      <span class="detail" part="detail"><slot></slot></span>
    </span>`}};B.styles=b`
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
  `,B=p([x("sx-provenance")],B);})();
