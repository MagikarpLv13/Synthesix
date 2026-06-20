var At=Object.defineProperty;var Et=Object.getOwnPropertyDescriptor;var u=(o,t,e,s)=>{for(var r=s>1?void 0:s?Et(t,e):t,i=o.length-1,n;i>=0;i--)(n=o[i])&&(r=(s?n(t,e,r):n(r))||r);return s&&r&&At(t,e,r),r};var B=globalThis,I=B.ShadowRoot&&(B.ShadyCSS===void 0||B.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,J=Symbol(),nt=new WeakMap,N=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==J)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(I&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=nt.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&nt.set(e,t))}return t}toString(){return this.cssText}},at=o=>new N(typeof o=="string"?o:o+"",void 0,J),$=(o,...t)=>{let e=o.length===1?o[0]:t.reduce((s,r,i)=>s+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+o[i+1],o[0]);return new N(e,o,J)},lt=(o,t)=>{if(I)o.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),r=B.litNonce;r!==void 0&&s.setAttribute("nonce",r),s.textContent=e.cssText,o.appendChild(s)}},Z=I?o=>o:o=>o instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return at(e)})(o):o;var{is:wt,defineProperty:St,getOwnPropertyDescriptor:Ct,getOwnPropertyNames:Pt,getOwnPropertySymbols:kt,getPrototypeOf:Ut}=Object,V=globalThis,ct=V.trustedTypes,Mt=ct?ct.emptyScript:"",Ot=V.reactiveElementPolyfillSupport,H=(o,t)=>o,T={toAttribute(o,t){switch(t){case Boolean:o=o?Mt:null;break;case Object:case Array:o=o==null?o:JSON.stringify(o)}return o},fromAttribute(o,t){let e=o;switch(t){case Boolean:e=o!==null;break;case Number:e=o===null?null:Number(o);break;case Object:case Array:try{e=JSON.parse(o)}catch{e=null}}return e}},W=(o,t)=>!wt(o,t),ht={attribute:!0,type:String,converter:T,reflect:!1,useDefault:!1,hasChanged:W};Symbol.metadata??=Symbol("metadata"),V.litPropertyMetadata??=new WeakMap;var b=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=ht){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),r=this.getPropertyDescriptor(t,s,e);r!==void 0&&St(this.prototype,t,r)}}static getPropertyDescriptor(t,e,s){let{get:r,set:i}=Ct(this.prototype,t)??{get(){return this[e]},set(n){this[e]=n}};return{get:r,set(n){let l=r?.call(this);i?.call(this,n),this.requestUpdate(t,l,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??ht}static _$Ei(){if(this.hasOwnProperty(H("elementProperties")))return;let t=Ut(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(H("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(H("properties"))){let e=this.properties,s=[...Pt(e),...kt(e)];for(let r of s)this.createProperty(r,e[r])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,r]of e)this.elementProperties.set(s,r)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let r=this._$Eu(e,s);r!==void 0&&this._$Eh.set(r,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let r of s)e.unshift(Z(r))}else t!==void 0&&e.push(Z(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return lt(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),r=this.constructor._$Eu(t,s);if(r!==void 0&&s.reflect===!0){let i=(s.converter?.toAttribute!==void 0?s.converter:T).toAttribute(e,s.type);this._$Em=t,i==null?this.removeAttribute(r):this.setAttribute(r,i),this._$Em=null}}_$AK(t,e){let s=this.constructor,r=s._$Eh.get(t);if(r!==void 0&&this._$Em!==r){let i=s.getPropertyOptions(r),n=typeof i.converter=="function"?{fromAttribute:i.converter}:i.converter?.fromAttribute!==void 0?i.converter:T;this._$Em=r;let l=n.fromAttribute(e,i.type);this[r]=l??this._$Ej?.get(r)??l,this._$Em=null}}requestUpdate(t,e,s,r=!1,i){if(t!==void 0){let n=this.constructor;if(r===!1&&(i=this[t]),s??=n.getPropertyOptions(t),!((s.hasChanged??W)(i,e)||s.useDefault&&s.reflect&&i===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:r,wrapped:i},n){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),i!==!0||n!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),r===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[r,i]of this._$Ep)this[r]=i;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[r,i]of s){let{wrapped:n}=i,l=this[r];n!==!0||this._$AL.has(r)||l===void 0||this.C(r,void 0,i,l)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};b.elementStyles=[],b.shadowRootOptions={mode:"open"},b[H("elementProperties")]=new Map,b[H("finalized")]=new Map,Ot?.({ReactiveElement:b}),(V.reactiveElementVersions??=[]).push("2.1.2");var st=globalThis,dt=o=>o,K=st.trustedTypes,pt=K?K.createPolicy("lit-html",{createHTML:o=>o}):void 0,$t="$lit$",_=`lit$${Math.random().toFixed(9).slice(2)}$`,bt="?"+_,Nt=`<${bt}>`,S=document,L=()=>S.createComment(""),j=o=>o===null||typeof o!="object"&&typeof o!="function",rt=Array.isArray,Ht=o=>rt(o)||typeof o?.[Symbol.iterator]=="function",G=`[ 	
\f\r]`,R=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ut=/-->/g,mt=/>/g,E=RegExp(`>|${G}(?:([^\\s"'>=/]+)(${G}*=${G}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),ft=/'/g,gt=/"/g,yt=/^(?:script|style|textarea|title)$/i,ot=o=>(t,...e)=>({_$litType$:o,strings:t,values:e}),g=ot(1),Wt=ot(2),Kt=ot(3),C=Symbol.for("lit-noChange"),d=Symbol.for("lit-nothing"),vt=new WeakMap,w=S.createTreeWalker(S,129);function _t(o,t){if(!rt(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return pt!==void 0?pt.createHTML(t):t}var Tt=(o,t)=>{let e=o.length-1,s=[],r,i=t===2?"<svg>":t===3?"<math>":"",n=R;for(let l=0;l<e;l++){let a=o[l],h,p,c=-1,v=0;for(;v<a.length&&(n.lastIndex=v,p=n.exec(a),p!==null);)v=n.lastIndex,n===R?p[1]==="!--"?n=ut:p[1]!==void 0?n=mt:p[2]!==void 0?(yt.test(p[2])&&(r=RegExp("</"+p[2],"g")),n=E):p[3]!==void 0&&(n=E):n===E?p[0]===">"?(n=r??R,c=-1):p[1]===void 0?c=-2:(c=n.lastIndex-p[2].length,h=p[1],n=p[3]===void 0?E:p[3]==='"'?gt:ft):n===gt||n===ft?n=E:n===ut||n===mt?n=R:(n=E,r=void 0);let y=n===E&&o[l+1].startsWith("/>")?" ":"";i+=n===R?a+Nt:c>=0?(s.push(h),a.slice(0,c)+$t+a.slice(c)+_+y):a+_+(c===-2?l:y)}return[_t(o,i+(o[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},q=class o{constructor({strings:t,_$litType$:e},s){let r;this.parts=[];let i=0,n=0,l=t.length-1,a=this.parts,[h,p]=Tt(t,e);if(this.el=o.createElement(h,s),w.currentNode=this.el.content,e===2||e===3){let c=this.el.content.firstChild;c.replaceWith(...c.childNodes)}for(;(r=w.nextNode())!==null&&a.length<l;){if(r.nodeType===1){if(r.hasAttributes())for(let c of r.getAttributeNames())if(c.endsWith($t)){let v=p[n++],y=r.getAttribute(c).split(_),D=/([.?@])?(.*)/.exec(v);a.push({type:1,index:i,name:D[2],strings:y,ctor:D[1]==="."?X:D[1]==="?"?Y:D[1]==="@"?tt:M}),r.removeAttribute(c)}else c.startsWith(_)&&(a.push({type:6,index:i}),r.removeAttribute(c));if(yt.test(r.tagName)){let c=r.textContent.split(_),v=c.length-1;if(v>0){r.textContent=K?K.emptyScript:"";for(let y=0;y<v;y++)r.append(c[y],L()),w.nextNode(),a.push({type:2,index:++i});r.append(c[v],L())}}}else if(r.nodeType===8)if(r.data===bt)a.push({type:2,index:i});else{let c=-1;for(;(c=r.data.indexOf(_,c+1))!==-1;)a.push({type:7,index:i}),c+=_.length-1}i++}}static createElement(t,e){let s=S.createElement("template");return s.innerHTML=t,s}};function U(o,t,e=o,s){if(t===C)return t;let r=s!==void 0?e._$Co?.[s]:e._$Cl,i=j(t)?void 0:t._$litDirective$;return r?.constructor!==i&&(r?._$AO?.(!1),i===void 0?r=void 0:(r=new i(o),r._$AT(o,e,s)),s!==void 0?(e._$Co??=[])[s]=r:e._$Cl=r),r!==void 0&&(t=U(o,r._$AS(o,t.values),r,s)),t}var Q=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,r=(t?.creationScope??S).importNode(e,!0);w.currentNode=r;let i=w.nextNode(),n=0,l=0,a=s[0];for(;a!==void 0;){if(n===a.index){let h;a.type===2?h=new z(i,i.nextSibling,this,t):a.type===1?h=new a.ctor(i,a.name,a.strings,this,t):a.type===6&&(h=new et(i,this,t)),this._$AV.push(h),a=s[++l]}n!==a?.index&&(i=w.nextNode(),n++)}return w.currentNode=S,r}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},z=class o{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,r){this.type=2,this._$AH=d,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=U(this,t,e),j(t)?t===d||t==null||t===""?(this._$AH!==d&&this._$AR(),this._$AH=d):t!==this._$AH&&t!==C&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Ht(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==d&&j(this._$AH)?this._$AA.nextSibling.data=t:this.T(S.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,r=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=q.createElement(_t(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===r)this._$AH.p(e);else{let i=new Q(r,this),n=i.u(this.options);i.p(e),this.T(n),this._$AH=i}}_$AC(t){let e=vt.get(t.strings);return e===void 0&&vt.set(t.strings,e=new q(t)),e}k(t){rt(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,r=0;for(let i of t)r===e.length?e.push(s=new o(this.O(L()),this.O(L()),this,this.options)):s=e[r],s._$AI(i),r++;r<e.length&&(this._$AR(s&&s._$AB.nextSibling,r),e.length=r)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=dt(t).nextSibling;dt(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},M=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,r,i){this.type=1,this._$AH=d,this._$AN=void 0,this.element=t,this.name=e,this._$AM=r,this.options=i,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=d}_$AI(t,e=this,s,r){let i=this.strings,n=!1;if(i===void 0)t=U(this,t,e,0),n=!j(t)||t!==this._$AH&&t!==C,n&&(this._$AH=t);else{let l=t,a,h;for(t=i[0],a=0;a<i.length-1;a++)h=U(this,l[s+a],e,a),h===C&&(h=this._$AH[a]),n||=!j(h)||h!==this._$AH[a],h===d?t=d:t!==d&&(t+=(h??"")+i[a+1]),this._$AH[a]=h}n&&!r&&this.j(t)}j(t){t===d?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},X=class extends M{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===d?void 0:t}},Y=class extends M{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==d)}},tt=class extends M{constructor(t,e,s,r,i){super(t,e,s,r,i),this.type=5}_$AI(t,e=this){if((t=U(this,t,e,0)??d)===C)return;let s=this._$AH,r=t===d&&s!==d||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,i=t!==d&&(s===d||r);r&&this.element.removeEventListener(this.name,this,s),i&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},et=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){U(this,t)}};var Rt=st.litHtmlPolyfillSupport;Rt?.(q,z),(st.litHtmlVersions??=[]).push("3.3.3");var xt=(o,t,e)=>{let s=e?.renderBefore??t,r=s._$litPart$;if(r===void 0){let i=e?.renderBefore??null;s._$litPart$=r=new z(t.insertBefore(L(),i),i,void 0,e??{})}return r._$AI(o),r};var it=globalThis,m=class extends b{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=xt(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return C}};m._$litElement$=!0,m.finalized=!0,it.litElementHydrateSupport?.({LitElement:m});var Lt=it.litElementPolyfillSupport;Lt?.({LitElement:m});(it.litElementVersions??=[]).push("4.2.2");var x=o=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(o,t)}):customElements.define(o,t)};var jt={attribute:!0,type:String,converter:T,reflect:!1,hasChanged:W},qt=(o=jt,t,e)=>{let{kind:s,metadata:r}=e,i=globalThis.litPropertyMetadata.get(r);if(i===void 0&&globalThis.litPropertyMetadata.set(r,i=new Map),s==="setter"&&((o=Object.create(o)).wrapped=!0),i.set(e.name,o),s==="accessor"){let{name:n}=e;return{set(l){let a=t.get.call(this);t.set.call(this,l),this.requestUpdate(n,a,o,!0,l)},init(l){return l!==void 0&&this.C(n,void 0,o,l),l}}}if(s==="setter"){let{name:n}=e;return function(l){let a=this[n];t.call(this,l),this.requestUpdate(n,a,o,!0,l)}}throw Error("Unsupported decorator location: "+s)};function f(o){return(t,e)=>typeof e=="object"?qt(o,t,e):((s,r,i)=>{let n=r.hasOwnProperty(i);return r.constructor.createProperty(i,s),n?Object.getOwnPropertyDescriptor(r,i):void 0})(o,t,e)}var O=class extends m{constructor(){super(...arguments);this.tone="neutral"}render(){return g`<span class="chip"><slot></slot></span>`}};O.styles=$`
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
  `,u([f({reflect:!0})],O.prototype,"tone",2),O=u([x("sx-chip")],O);var P=class extends m{constructor(){super(...arguments);this.accent="none";this.triage=!1}willUpdate(e){e.has("triage")&&(this.triage?(this.setAttribute("data-triage-item",""),this.hasAttribute("tabindex")||this.setAttribute("tabindex","0")):this.removeAttribute("data-triage-item"))}render(){return g`
      <article class="card" part="card">
        <div class="body" part="body">
          <div class="head" part="head">
            <slot name="title"></slot>
            <slot name="domain"></slot>
          </div>
          <div class="snippet" part="snippet">
            <slot name="snippet"></slot>
          </div>
          <div class="extra" part="extra">
            <slot name="extra"></slot>
          </div>
          <div class="meta" part="meta">
            <slot name="meta"></slot>
          </div>
        </div>
        <div class="actions" part="actions">
          <slot name="actions"></slot>
        </div>
      </article>
    `}};P.styles=$`
    :host {
      display: block;
      outline: none;
    }

    .card {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: var(--space-4, 16px);
      padding: var(--space-3, 12px) var(--space-4, 16px);
      border: 1px solid var(--line, #cbd5e1);
      border-left: 3px solid var(--line, #cbd5e1);
      border-radius: var(--radius-md, 8px);
      background: var(--surface, #ffffff);
      color: var(--text, #0f172a);
      transition:
        border-color 120ms ease,
        box-shadow 120ms ease;
    }

    :host([accent="strong"]) .card {
      border-left-color: var(--success, #16a34a);
    }

    :host([accent="good"]) .card {
      border-left-color: var(--accent, #2563eb);
    }

    :host([accent="moderate"]) .card {
      border-left-color: var(--warning, #d97706);
    }

    :host([accent="weak"]) .card {
      border-left-color: var(--line, #cbd5e1);
    }

    :host(:hover) .card {
      border-color: var(--accent, #2563eb);
      box-shadow: var(--shadow-soft, 0 8px 22px rgba(15, 23, 42, 0.08));
    }

    :host(:focus-visible) .card,
    :host(:focus) .card {
      border-color: var(--accent, #2563eb);
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }

    .body {
      flex: 1 1 auto;
      min-width: 0;
    }

    .head {
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      gap: 4px var(--space-3, 12px);
      min-width: 0;
    }

    .snippet {
      margin: 0;
    }

    .extra {
      display: contents;
    }

    .meta {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: var(--space-2, 8px);
    }

    .actions {
      display: flex;
      flex: 0 0 auto;
      align-items: center;
      gap: 6px;
    }

    ::slotted([slot="title"]) {
      color: var(--text, #0f172a);
      font-size: 15px;
      font-weight: 500;
      overflow-wrap: anywhere;
      text-decoration: none;
    }

    ::slotted([slot="title"]:hover) {
      color: var(--accent, #2563eb);
      text-decoration: underline;
    }

    ::slotted([slot="domain"]) {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      color: var(--muted, #64748b);
      font-size: 12px;
    }

    ::slotted([slot="snippet"]) {
      margin: 4px 0 8px;
      color: var(--muted, #64748b);
      font-size: 13px;
      line-height: 1.5;
      overflow-wrap: anywhere;
    }

    @media (max-width: 720px) {
      .card {
        flex-direction: column;
      }

      .actions {
        width: 100%;
      }
    }
  `,u([f({reflect:!0})],P.prototype,"accent",2),u([f({type:Boolean,reflect:!0})],P.prototype,"triage",2),P=u([x("sx-result-card")],P);var k=class extends m{constructor(){super(...arguments);this.level="none";this.expandable=!1}render(){let e=g`<span class="value" part="value"><slot></slot></span>`;return this.expandable?g`
      <details class="score" part="score">
        <summary part="summary">${e}</summary>
        <ul class="list" part="breakdown">
          <slot name="breakdown"></slot>
        </ul>
        <small class="note" part="note">
          <slot name="note"></slot>
        </small>
      </details>
    `:g`<span class="score" part="score">${e}</span>`}};k.styles=$`
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
  `,u([f({reflect:!0})],k.prototype,"level",2),u([f({type:Boolean,reflect:!0})],k.prototype,"expandable",2),k=u([x("sx-score")],k);var A=class extends m{constructor(){super(...arguments);this.tone="muted";this.removable=!1;this.removeLabel="Remove"}_remove(){this.dispatchEvent(new CustomEvent("sx-tag-remove",{bubbles:!0,composed:!0}))}render(){return g`<span class="tag" part="tag">
      <slot></slot>
      ${this.removable?g`<button
            class="remove"
            part="remove"
            type="button"
            aria-label=${this.removeLabel}
            @click=${this._remove}
          >
            &times;
          </button>`:null}
    </span>`}};A.styles=$`
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
  `,u([f({reflect:!0})],A.prototype,"tone",2),u([f({type:Boolean,reflect:!0})],A.prototype,"removable",2),u([f({attribute:"remove-label"})],A.prototype,"removeLabel",2),A=u([x("sx-tag")],A);
