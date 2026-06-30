"use strict";(()=>{var zt=Object.defineProperty;var Rt=Object.getOwnPropertyDescriptor;var u=(o,t,e,s)=>{for(var i=s>1?void 0:s?Rt(t,e):t,r=o.length-1,n;r>=0;r--)(n=o[r])&&(i=(s?n(t,e,i):n(i))||i);return s&&i&&zt(t,e,i),i};var Q=globalThis,tt=Q.ShadowRoot&&(Q.ShadyCSS===void 0||Q.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,ot=Symbol(),vt=new WeakMap,V=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==ot)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(tt&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=vt.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&vt.set(e,t))}return t}toString(){return this.cssText}},bt=o=>new V(typeof o=="string"?o:o+"",void 0,ot),b=(o,...t)=>{let e=o.length===1?o[0]:t.reduce((s,i,r)=>s+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+o[r+1],o[0]);return new V(e,o,ot)},yt=(o,t)=>{if(tt)o.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),i=Q.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=e.cssText,o.appendChild(s)}},nt=tt?o=>o:o=>o instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return bt(e)})(o):o;var{is:Gt,defineProperty:qt,getOwnPropertyDescriptor:Dt,getOwnPropertyNames:Vt,getOwnPropertySymbols:jt,getPrototypeOf:It}=Object,et=globalThis,_t=et.trustedTypes,Bt=_t?_t.emptyScript:"",Wt=et.reactiveElementPolyfillSupport,j=(o,t)=>o,I={toAttribute(o,t){switch(t){case Boolean:o=o?Bt:null;break;case Object:case Array:o=o==null?o:JSON.stringify(o)}return o},fromAttribute(o,t){let e=o;switch(t){case Boolean:e=o!==null;break;case Number:e=o===null?null:Number(o);break;case Object:case Array:try{e=JSON.parse(o)}catch{e=null}}return e}},st=(o,t)=>!Gt(o,t),xt={attribute:!0,type:String,converter:I,reflect:!1,useDefault:!1,hasChanged:st};Symbol.metadata??=Symbol("metadata"),et.litPropertyMetadata??=new WeakMap;var A=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=xt){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(t,s,e);i!==void 0&&qt(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){let{get:i,set:r}=Dt(this.prototype,t)??{get(){return this[e]},set(n){this[e]=n}};return{get:i,set(n){let c=i?.call(this);r?.call(this,n),this.requestUpdate(t,c,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??xt}static _$Ei(){if(this.hasOwnProperty(j("elementProperties")))return;let t=It(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(j("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(j("properties"))){let e=this.properties,s=[...Vt(e),...jt(e)];for(let i of s)this.createProperty(i,e[i])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,i]of e)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let i=this._$Eu(e,s);i!==void 0&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let i of s)e.unshift(nt(i))}else t!==void 0&&e.push(nt(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return yt(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),i=this.constructor._$Eu(t,s);if(i!==void 0&&s.reflect===!0){let r=(s.converter?.toAttribute!==void 0?s.converter:I).toAttribute(e,s.type);this._$Em=t,r==null?this.removeAttribute(i):this.setAttribute(i,r),this._$Em=null}}_$AK(t,e){let s=this.constructor,i=s._$Eh.get(t);if(i!==void 0&&this._$Em!==i){let r=s.getPropertyOptions(i),n=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:I;this._$Em=i;let c=n.fromAttribute(e,r.type);this[i]=c??this._$Ej?.get(i)??c,this._$Em=null}}requestUpdate(t,e,s,i=!1,r){if(t!==void 0){let n=this.constructor;if(i===!1&&(r=this[t]),s??=n.getPropertyOptions(t),!((s.hasChanged??st)(r,e)||s.useDefault&&s.reflect&&r===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:i,wrapped:r},n){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),r!==!0||n!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),i===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,r]of this._$Ep)this[i]=r;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,r]of s){let{wrapped:n}=r,c=this[i];n!==!0||this._$AL.has(i)||c===void 0||this.C(i,void 0,r,c)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};A.elementStyles=[],A.shadowRootOptions={mode:"open"},A[j("elementProperties")]=new Map,A[j("finalized")]=new Map,Wt?.({ReactiveElement:A}),(et.reactiveElementVersions??=[]).push("2.1.2");var ut=globalThis,$t=o=>o,it=ut.trustedTypes,wt=it?it.createPolicy("lit-html",{createHTML:o=>o}):void 0,Ct="$lit$",S=`lit$${Math.random().toFixed(9).slice(2)}$`,Lt="?"+S,Yt=`<${Lt}>`,T=document,W=()=>T.createComment(""),Y=o=>o===null||typeof o!="object"&&typeof o!="function",mt=Array.isArray,Xt=o=>mt(o)||typeof o?.[Symbol.iterator]=="function",at=`[ 	
\f\r]`,B=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,At=/-->/g,Et=/>/g,P=RegExp(`>|${at}(?:([^\\s"'>=/]+)(${at}*=${at}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),kt=/'/g,St=/"/g,Pt=/^(?:script|style|textarea|title)$/i,ft=o=>(t,...e)=>({_$litType$:o,strings:t,values:e}),m=ft(1),ne=ft(2),ae=ft(3),N=Symbol.for("lit-noChange"),x=Symbol.for("lit-nothing"),Mt=new WeakMap,O=T.createTreeWalker(T,129);function Ot(o,t){if(!mt(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return wt!==void 0?wt.createHTML(t):t}var Kt=(o,t)=>{let e=o.length-1,s=[],i,r=t===2?"<svg>":t===3?"<math>":"",n=B;for(let c=0;c<e;c++){let a=o[c],p,d,h=-1,l=0;for(;l<a.length&&(n.lastIndex=l,d=n.exec(a),d!==null);)l=n.lastIndex,n===B?d[1]==="!--"?n=At:d[1]!==void 0?n=Et:d[2]!==void 0?(Pt.test(d[2])&&(i=RegExp("</"+d[2],"g")),n=P):d[3]!==void 0&&(n=P):n===P?d[0]===">"?(n=i??B,h=-1):d[1]===void 0?h=-2:(h=n.lastIndex-d[2].length,p=d[1],n=d[3]===void 0?P:d[3]==='"'?St:kt):n===St||n===kt?n=P:n===At||n===Et?n=B:(n=P,i=void 0);let f=n===P&&o[c+1].startsWith("/>")?" ":"";r+=n===B?a+Yt:h>=0?(s.push(p),a.slice(0,h)+Ct+a.slice(h)+S+f):a+S+(h===-2?c:f)}return[Ot(o,r+(o[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},X=class o{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let r=0,n=0,c=t.length-1,a=this.parts,[p,d]=Kt(t,e);if(this.el=o.createElement(p,s),O.currentNode=this.el.content,e===2||e===3){let h=this.el.content.firstChild;h.replaceWith(...h.childNodes)}for(;(i=O.nextNode())!==null&&a.length<c;){if(i.nodeType===1){if(i.hasAttributes())for(let h of i.getAttributeNames())if(h.endsWith(Ct)){let l=d[n++],f=i.getAttribute(h).split(S),_=/([.?@])?(.*)/.exec(l);a.push({type:1,index:r,name:_[2],strings:f,ctor:_[1]==="."?ct:_[1]==="?"?dt:_[1]==="@"?pt:G}),i.removeAttribute(h)}else h.startsWith(S)&&(a.push({type:6,index:r}),i.removeAttribute(h));if(Pt.test(i.tagName)){let h=i.textContent.split(S),l=h.length-1;if(l>0){i.textContent=it?it.emptyScript:"";for(let f=0;f<l;f++)i.append(h[f],W()),O.nextNode(),a.push({type:2,index:++r});i.append(h[l],W())}}}else if(i.nodeType===8)if(i.data===Lt)a.push({type:2,index:r});else{let h=-1;for(;(h=i.data.indexOf(S,h+1))!==-1;)a.push({type:7,index:r}),h+=S.length-1}r++}}static createElement(t,e){let s=T.createElement("template");return s.innerHTML=t,s}};function R(o,t,e=o,s){if(t===N)return t;let i=s!==void 0?e._$Co?.[s]:e._$Cl,r=Y(t)?void 0:t._$litDirective$;return i?.constructor!==r&&(i?._$AO?.(!1),r===void 0?i=void 0:(i=new r(o),i._$AT(o,e,s)),s!==void 0?(e._$Co??=[])[s]=i:e._$Cl=i),i!==void 0&&(t=R(o,i._$AS(o,t.values),i,s)),t}var lt=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,i=(t?.creationScope??T).importNode(e,!0);O.currentNode=i;let r=O.nextNode(),n=0,c=0,a=s[0];for(;a!==void 0;){if(n===a.index){let p;a.type===2?p=new K(r,r.nextSibling,this,t):a.type===1?p=new a.ctor(r,a.name,a.strings,this,t):a.type===6&&(p=new ht(r,this,t)),this._$AV.push(p),a=s[++c]}n!==a?.index&&(r=O.nextNode(),n++)}return O.currentNode=T,i}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},K=class o{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,i){this.type=2,this._$AH=x,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=R(this,t,e),Y(t)?t===x||t==null||t===""?(this._$AH!==x&&this._$AR(),this._$AH=x):t!==this._$AH&&t!==N&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Xt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==x&&Y(this._$AH)?this._$AA.nextSibling.data=t:this.T(T.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,i=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=X.createElement(Ot(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(e);else{let r=new lt(i,this),n=r.u(this.options);r.p(e),this.T(n),this._$AH=r}}_$AC(t){let e=Mt.get(t.strings);return e===void 0&&Mt.set(t.strings,e=new X(t)),e}k(t){mt(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,i=0;for(let r of t)i===e.length?e.push(s=new o(this.O(W()),this.O(W()),this,this.options)):s=e[i],s._$AI(r),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=$t(t).nextSibling;$t(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},G=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,i,r){this.type=1,this._$AH=x,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=r,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=x}_$AI(t,e=this,s,i){let r=this.strings,n=!1;if(r===void 0)t=R(this,t,e,0),n=!Y(t)||t!==this._$AH&&t!==N,n&&(this._$AH=t);else{let c=t,a,p;for(t=r[0],a=0;a<r.length-1;a++)p=R(this,c[s+a],e,a),p===N&&(p=this._$AH[a]),n||=!Y(p)||p!==this._$AH[a],p===x?t=x:t!==x&&(t+=(p??"")+r[a+1]),this._$AH[a]=p}n&&!i&&this.j(t)}j(t){t===x?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},ct=class extends G{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===x?void 0:t}},dt=class extends G{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==x)}},pt=class extends G{constructor(t,e,s,i,r){super(t,e,s,i,r),this.type=5}_$AI(t,e=this){if((t=R(this,t,e,0)??x)===N)return;let s=this._$AH,i=t===x&&s!==x||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==x&&(s===x||i);i&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},ht=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){R(this,t)}};var Ft=ut.litHtmlPolyfillSupport;Ft?.(X,K),(ut.litHtmlVersions??=[]).push("3.3.3");var Tt=(o,t,e)=>{let s=e?.renderBefore??t,i=s._$litPart$;if(i===void 0){let r=e?.renderBefore??null;s._$litPart$=i=new K(t.insertBefore(W(),r),r,void 0,e??{})}return i._$AI(o),i};var gt=globalThis,g=class extends A{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=Tt(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return N}};g._$litElement$=!0,g.finalized=!0,gt.litElementHydrateSupport?.({LitElement:g});var Zt=gt.litElementPolyfillSupport;Zt?.({LitElement:g});(gt.litElementVersions??=[]).push("4.2.2");var y=o=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(o,t)}):customElements.define(o,t)};var Jt={attribute:!0,type:String,converter:I,reflect:!1,hasChanged:st},Qt=(o=Jt,t,e)=>{let{kind:s,metadata:i}=e,r=globalThis.litPropertyMetadata.get(i);if(r===void 0&&globalThis.litPropertyMetadata.set(i,r=new Map),s==="setter"&&((o=Object.create(o)).wrapped=!0),r.set(e.name,o),s==="accessor"){let{name:n}=e;return{set(c){let a=t.get.call(this);t.set.call(this,c),this.requestUpdate(n,a,o,!0,c)},init(c){return c!==void 0&&this.C(n,void 0,o,c),c}}}if(s==="setter"){let{name:n}=e;return function(c){let a=this[n];t.call(this,c),this.requestUpdate(n,a,o,!0,c)}}throw Error("Unsupported decorator location: "+s)};function v(o){return(t,e)=>typeof e=="object"?Qt(o,t,e):((s,i,r)=>{let n=i.hasOwnProperty(r);return i.constructor.createProperty(r,s),n?Object.getOwnPropertyDescriptor(i,r):void 0})(o,t,e)}function Nt(o){return v({...o,state:!0,attribute:!1})}var q=class extends g{constructor(){super(...arguments);this.tone="neutral"}render(){return m`<span class="chip"><slot></slot></span>`}};q.styles=b`
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
  `,u([v({reflect:!0})],q.prototype,"tone",2),q=u([y("sx-chip")],q);var H=class extends g{constructor(){super(...arguments);this.accent="none";this.triage=!1}willUpdate(e){e.has("triage")&&(this.triage?(this.setAttribute("data-triage-item",""),this.hasAttribute("tabindex")||this.setAttribute("tabindex","0")):this.removeAttribute("data-triage-item"))}render(){return m`
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
  `,u([v({reflect:!0})],H.prototype,"accent",2),u([v({type:Boolean,reflect:!0})],H.prototype,"triage",2),H=u([y("sx-result-card")],H);var U=class extends g{constructor(){super(...arguments);this.level="none";this.expandable=!1}render(){let e=m`<span class="value" part="value"><slot></slot></span>`;return this.expandable?m`
      <details class="score" part="score">
        <summary part="summary">${e}</summary>
        <ul class="list" part="breakdown">
          <slot name="breakdown"></slot>
        </ul>
        <small class="note" part="note">
          <slot name="note"></slot>
        </small>
      </details>
    `:m`<span class="score" part="score">${e}</span>`}};U.styles=b`
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
  `,u([v({reflect:!0})],U.prototype,"level",2),u([v({type:Boolean,reflect:!0})],U.prototype,"expandable",2),U=u([y("sx-score")],U);var M=class extends g{constructor(){super(...arguments);this.tone="muted";this.removable=!1;this.removeLabel="Remove"}_remove(){this.dispatchEvent(new CustomEvent("sx-tag-remove",{bubbles:!0,composed:!0}))}render(){return m`<span class="tag" part="tag">
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
    </span>`}};M.styles=b`
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
  `,u([v({reflect:!0})],M.prototype,"tone",2),u([v({type:Boolean,reflect:!0})],M.prototype,"removable",2),u([v({attribute:"remove-label"})],M.prototype,"removeLabel",2),M=u([y("sx-tag")],M);var F=class extends g{render(){return m`<span class="provenance" part="provenance">
      <slot name="icon"></slot>
      <span class="label" part="label"><slot name="label"></slot></span>
      <span class="detail" part="detail"><slot></slot></span>
    </span>`}};F.styles=b`
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
  `,F=u([y("sx-provenance")],F);var D=class extends g{constructor(){super(...arguments);this.status="pending"}render(){return m`<span
      class="badge"
      part="badge"
      role="status"
      aria-live="polite"
    >
      <slot></slot>
    </span>`}};D.styles=b`
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
  `,u([v({reflect:!0})],D.prototype,"status",2),D=u([y("sx-evidence-badge")],D);var C=class extends g{constructor(){super(...arguments);this.selected="";this.pane="list";this.backLabel="Back to list"}get _items(){return Array.from(this.querySelectorAll("[data-inspector-item]"))}get _panels(){return Array.from(this.querySelectorAll("[data-inspector-panel]"))}_valueOf(e){return e.getAttribute("data-inspector-item")??""}firstUpdated(){if(!this.selected){let e=this._items[0];e&&(this.selected=this._valueOf(e))}this._sync()}updated(e){e.has("selected")&&this._sync()}_sync(){let e=this.selected;for(let s of this._items)this._valueOf(s)===e?s.setAttribute("aria-current","true"):s.removeAttribute("aria-current");for(let s of this._panels)s.hidden=s.getAttribute("data-inspector-panel")!==e}_select(e,s=!1){if(e===this.selected){this.pane="detail";return}let i=this.selected;this.selected=e,this.pane="detail",this.dispatchEvent(new CustomEvent("sx-inspector-select",{detail:{value:e,previous:i},bubbles:!0,composed:!0})),s&&this.updateComplete.then(()=>{this._items.find(n=>this._valueOf(n)===e)?.focus()})}_onListClick(e){let i=e.target?.closest("[data-inspector-item]");i&&this.contains(i)&&this._select(this._valueOf(i))}_onListKeydown(e){if(!["ArrowDown","ArrowUp","Home","End"].includes(e.key))return;let i=this._items;if(!i.length)return;let r=i.findIndex(c=>this._valueOf(c)===this.selected),n=r;e.key==="ArrowDown"?n=Math.min(i.length-1,r+1):e.key==="ArrowUp"?n=Math.max(0,r-1):e.key==="Home"?n=0:e.key==="End"&&(n=i.length-1),n!==r&&(e.preventDefault(),this._select(this._valueOf(i[n]),!0))}_onBack(){this.pane="list",this.updateComplete.then(()=>{this._items.find(s=>this._valueOf(s)===this.selected)?.focus()})}_onSlotChange(){if(!this.selected){let e=this._items[0];if(e){this.selected=e.getAttribute("data-inspector-item")??"";return}}this._sync()}render(){return m`
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
    `}};C.styles=b`
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
  `,u([v({reflect:!0})],C.prototype,"selected",2),u([v({reflect:!0})],C.prototype,"pane",2),u([v({attribute:"back-label"})],C.prototype,"backLabel",2),C=u([y("sx-inspector")],C);var L=class extends g{constructor(){super(...arguments);this.kind="";this.confidence="";this.status="candidate"}_onOptionalSlot(e){let s=e.target,i=s.parentElement;if(!i)return;let r=s.assignedNodes({flatten:!0}).some(n=>n.nodeType===Node.ELEMENT_NODE||(n.textContent??"").trim().length>0);i.hidden=!r}render(){return m`
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
    `}};L.styles=b`
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
  `,u([v()],L.prototype,"kind",2),u([v()],L.prototype,"confidence",2),u([v({reflect:!0})],L.prototype,"status",2),L=u([y("sx-entity")],L);var Z="http://www.w3.org/2000/svg",Ht={personne:"#38bdf8",entreprise:"#a78bfa",organisation:"#a78bfa",lieu:"#34d399",adresse:"#34d399",\u00E9v\u00E9nement:"#fbbf24",evenement:"#fbbf24",document:"#f472b6",identifiant:"#f59e0b"},Ut=["#38bdf8","#a78bfa","#34d399","#fbbf24","#f472b6","#22d3ee","#c084fc"];function te(o){let t=(o??"").trim().toLowerCase();if(t&&Ht[t])return Ht[t];if(!t)return"#94a3b8";let e=0;for(let s=0;s<t.length;s+=1)e=e*31+t.charCodeAt(s)|0;return Ut[Math.abs(e)%Ut.length]}var z=class extends g{constructor(){super(...arguments);this.data=null;this._empty=!1;this._particles=[];this._links=[];this._byId=new Map;this._legend=[];this._k=1;this._tx=0;this._ty=0;this._width=0;this._height=0;this._resizeObs=null;this._laidOut=!1;this._mode="idle";this._dragParticle=null;this._startX=0;this._startY=0;this._moved=!1;this._activeId=null;this._onWheel=e=>{e.preventDefault();let s=this.getBoundingClientRect(),i=e.deltaY<0?1.12:1/1.12;this._zoomBy(i,e.clientX-s.left,e.clientY-s.top)};this._onPointerDown=e=>{if(e.button!==0)return;let i=e.target.closest(".node");if(this._startX=e.clientX,this._startY=e.clientY,this._moved=!1,this._svg?.setPointerCapture(e.pointerId),i?.dataset.id){let r=this._byId.get(i.dataset.id);r&&(this._mode="node",this._dragParticle=r,r.fixed=!0)}else this._mode="pan",this._svg?.classList.add("is-panning");window.addEventListener("pointermove",this._onPointerMove),window.addEventListener("pointerup",this._onPointerUp)};this._onPointerMove=e=>{let s=e.clientX-this._startX,i=e.clientY-this._startY;if(!this._moved&&Math.hypot(s,i)>4&&(this._moved=!0),this._mode==="pan")this._tx+=e.movementX,this._ty+=e.movementY,this._draw();else if(this._mode==="node"&&this._dragParticle){let r=this._toWorld(e.clientX,e.clientY);this._dragParticle.x=r.x,this._dragParticle.y=r.y,this._draw()}};this._onPointerUp=e=>{if(window.removeEventListener("pointermove",this._onPointerMove),window.removeEventListener("pointerup",this._onPointerUp),this._svg?.classList.remove("is-panning"),this._mode==="node"&&this._dragParticle){let s=this._dragParticle;s.fixed=!1,this._moved||this._select(s.node.id)}this._mode="idle",this._dragParticle=null}}get _svg(){return this.renderRoot.querySelector(".stage")}get _viewport(){return this.renderRoot.querySelector(".viewport")}get _edgesG(){return this.renderRoot.querySelector(".edges")}get _nodesG(){return this.renderRoot.querySelector(".nodes")}connectedCallback(){super.connectedCallback(),this.data||(this.data=this._readInlineData())}disconnectedCallback(){super.disconnectedCallback(),this._resizeObs?.disconnect(),this._resizeObs=null}firstUpdated(){let e=this._svg;e&&(e.addEventListener("wheel",this._onWheel,{passive:!1}),e.addEventListener("pointerdown",this._onPointerDown)),this._resizeObs=new ResizeObserver(s=>{let i=s[0]?.contentRect;i&&(this._width=i.width,this._height=i.height,!this._laidOut&&this._width>0&&this._height>0&&this._build())}),this._resizeObs.observe(this)}updated(e){e.has("data")&&(this._laidOut=!1,this._width>0&&this._height>0&&this._build())}_readInlineData(){let e=this.querySelector("script[data-graph-data]");if(!e?.textContent)return null;try{let s=JSON.parse(e.textContent);if(Array.isArray(s.nodes))return s}catch{}return null}_build(){let e=this._edgesG,s=this._nodesG;if(!e||!s)return;this.data||(this.data=this._readInlineData()),e.replaceChildren(),s.replaceChildren(),this._particles=[],this._links=[],this._byId.clear();let i=this.data?.nodes??[],r=this.data?.edges??[];if(this._empty=i.length===0,this._empty){this._laidOut=!0;return}let n=new Map,c=[],a=new Set(i.map(l=>l.id));for(let l of r)l.source!==l.target&&(!a.has(l.source)||!a.has(l.target)||(c.push(l),n.set(l.source,(n.get(l.source)??0)+1),n.set(l.target,(n.get(l.target)??0)+1)));let p=i.length,d=50*Math.sqrt(p)+60,h=new Map;i.forEach((l,f)=>{let _=n.get(l.id)??0,w=te(l.category);l.category&&h.set(l.category,w);let $=Math.random()*Math.PI*2,E=Math.sqrt(Math.random())*d,k={node:l,x:Math.cos($)*E,y:Math.sin($)*E,vx:0,vy:0,r:8+Math.min(14,_*2.2),degree:_,fixed:!1,el:this._makeNode(l,w,_),circle:null};k.circle=k.el.querySelector("circle"),this._particles.push(k),this._byId.set(l.id,k),s.appendChild(k.el)});for(let l of c){let f=this._byId.get(l.source),_=this._byId.get(l.target);if(!f||!_)continue;let w=document.createElementNS(Z,"line");w.setAttribute("class","edge"),w.setAttribute("marker-end","url(#sx-graph-arrow)"),e.appendChild(w);let $=null;l.label&&($=document.createElementNS(Z,"text"),$.setAttribute("class","edge-label"),$.setAttribute("text-anchor","middle"),$.textContent=l.label,e.appendChild($)),this._links.push({edge:l,a:f,b:_,line:w,label:$})}this._legend=[...h.entries()].map(([l,f])=>({label:l,color:f})),this._laidOut=!0,this._settle(),this.fit(),this.requestUpdate()}_makeNode(e,s,i){let r=document.createElementNS(Z,"g");r.setAttribute("class","node"),r.setAttribute("tabindex","0"),r.setAttribute("role","button"),r.setAttribute("aria-label",`${e.label}${e.category?` (${e.category})`:""}`),r.dataset.id=e.id;let n=document.createElementNS(Z,"circle"),c=8+Math.min(14,i*2.2);n.setAttribute("r",String(c)),n.setAttribute("fill",s),r.appendChild(n);let a=document.createElementNS(Z,"text");a.setAttribute("text-anchor","middle"),a.setAttribute("dy",String(-c-6));let p=e.label.length>28?`${e.label.slice(0,27)}\u2026`:e.label;return a.textContent=p,r.appendChild(a),r.addEventListener("keydown",d=>{(d.key==="Enter"||d.key===" ")&&(d.preventDefault(),this._select(e.id))}),r.addEventListener("pointerenter",()=>this._highlight(e.id)),r.addEventListener("pointerleave",()=>this._highlight(null)),r.addEventListener("focus",()=>this._highlight(e.id)),r.addEventListener("blur",()=>this._highlight(null)),r}_step(e){let s=this._particles,i=s.length,r=7e3,n=.012;for(let a=0;a<i;a+=1){let p=s[a];for(let d=a+1;d<i;d+=1){let h=s[d],l=p.x-h.x,f=p.y-h.y,_=l*l+f*f;_<.01&&(l=Math.random()-.5,f=Math.random()-.5,_=l*l+f*f);let w=Math.sqrt(_),$=Math.min(r/_,90),E=l/w*$,k=f/w*$;p.vx+=E,p.vy+=k,h.vx-=E,h.vy-=k}p.vx-=p.x*n,p.vy-=p.y*n}for(let a of this._links){let{a:p,b:d}=a,h=d.x-p.x,l=d.y-p.y,f=Math.sqrt(h*h+l*l)||1,_=150+p.r+d.r,w=(f-_)*.06,$=h/f*w,E=l/f*w;p.vx+=$,p.vy+=E,d.vx-=$,d.vy-=E}let c=.85;for(let a of s){if(a.fixed){a.vx=0,a.vy=0;continue}a.vx*=c,a.vy*=c,a.x+=a.vx*e,a.y+=a.vy*e}}_settle(){let e=1;for(let s=0;s<450&&e>.004;s+=1)this._step(e),e*=.985;this._draw()}_draw(){let e=this._viewport;e&&e.setAttribute("transform",`translate(${this._tx} ${this._ty}) scale(${this._k})`);for(let s of this._particles)s.el.setAttribute("transform",`translate(${s.x} ${s.y})`);for(let s of this._links){let{a:i,b:r,line:n,label:c}=s,a=r.x-i.x,p=r.y-i.y,d=Math.sqrt(a*a+p*p)||1,h=a/d,l=p/d;n.setAttribute("x1",String(i.x+h*i.r)),n.setAttribute("y1",String(i.y+l*i.r)),n.setAttribute("x2",String(r.x-h*(r.r+6))),n.setAttribute("y2",String(r.y-l*(r.r+6))),c&&(c.setAttribute("x",String((i.x+r.x)/2)),c.setAttribute("y",String((i.y+r.y)/2)))}}fit(){if(this._particles.length===0||this._width===0)return;let e=1/0,s=1/0,i=-1/0,r=-1/0;for(let d of this._particles)e=Math.min(e,d.x-d.r),s=Math.min(s,d.y-d.r),i=Math.max(i,d.x+d.r),r=Math.max(r,d.y+d.r);let n=48,c=i-e||1,a=r-s||1,p=Math.min((this._width-n*2)/c,(this._height-n*2)/a,1.6);this._k=Math.max(.1,p),this._tx=this._width/2-(e+i)/2*this._k,this._ty=this._height/2-(s+r)/2*this._k,this._draw()}_zoomBy(e,s,i){let r=s??this._width/2,n=i??this._height/2,c=Math.max(.1,Math.min(4,this._k*e));this._tx=r-(r-this._tx)*c/this._k,this._ty=n-(n-this._ty)*c/this._k,this._k=c,this._draw()}_toWorld(e,s){let i=this.getBoundingClientRect(),r=e-i.left,n=s-i.top;return{x:(r-this._tx)/this._k,y:(n-this._ty)/this._k}}_select(e){this.dispatchEvent(new CustomEvent("sx-entity-select",{detail:{id:e},bubbles:!0,composed:!0}))}_highlight(e){if(e===this._activeId)return;this._activeId=e;let s=this._svg;if(!s)return;if(!e){s.classList.remove("is-hovering");for(let r of this._particles)r.el.classList.remove("is-active");for(let r of this._links)r.line.classList.remove("is-active"),r.label?.classList.remove("is-active");return}let i=new Set([e]);for(let r of this._links){let n=r.a.node.id===e||r.b.node.id===e;r.line.classList.toggle("is-active",n),r.label?.classList.toggle("is-active",n),n&&(i.add(r.a.node.id),i.add(r.b.node.id))}for(let r of this._particles)r.el.classList.toggle("is-active",i.has(r.node.id));s.classList.add("is-hovering")}render(){return m`
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
            </div>
            ${this._legend.length?m`<div class="legend">
                  ${this._legend.map(e=>m`<span><i style=${`background:${e.color}`}></i>${e.label}</span>`)}
                </div>`:null}
          `}
    `}};z.styles=b`
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
  `,u([v({attribute:!1})],z.prototype,"data",2),u([Nt()],z.prototype,"_empty",2),z=u([y("sx-entity-graph")],z);var J=class extends g{render(){return m`<div class="property" part="property">
      <span class="label" part="label"><slot name="label"></slot></span>
      <span class="value" part="value"><slot></slot></span>
      <span class="actions" part="actions"><slot name="actions"></slot></span>
    </div>`}};J.styles=b`
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
  `,J=u([y("sx-property")],J);})();
