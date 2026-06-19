var At=Object.defineProperty;var bt=Object.getOwnPropertyDescriptor;var b=(o,t,e,s)=>{for(var r=s>1?void 0:s?bt(t,e):t,i=o.length-1,n;i>=0;i--)(n=o[i])&&(r=(s?n(t,e,r):n(r))||r);return s&&r&&At(t,e,r),r};var j=globalThis,q=j.ShadowRoot&&(j.ShadyCSS===void 0||j.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,K=Symbol(),ot=new WeakMap,C=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==K)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(q&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=ot.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&ot.set(e,t))}return t}toString(){return this.cssText}},it=o=>new C(typeof o=="string"?o:o+"",void 0,K),P=(o,...t)=>{let e=o.length===1?o[0]:t.reduce((s,r,i)=>s+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+o[i+1],o[0]);return new C(e,o,K)},nt=(o,t)=>{if(q)o.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),r=j.litNonce;r!==void 0&&s.setAttribute("nonce",r),s.textContent=e.cssText,o.appendChild(s)}},F=q?o=>o:o=>o instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return it(e)})(o):o;var{is:xt,defineProperty:Et,getOwnPropertyDescriptor:St,getOwnPropertyNames:wt,getOwnPropertySymbols:Ct,getPrototypeOf:Pt}=Object,D=globalThis,at=D.trustedTypes,Ut=at?at.emptyScript:"",Ot=D.reactiveElementPolyfillSupport,U=(o,t)=>o,O={toAttribute(o,t){switch(t){case Boolean:o=o?Ut:null;break;case Object:case Array:o=o==null?o:JSON.stringify(o)}return o},fromAttribute(o,t){let e=o;switch(t){case Boolean:e=o!==null;break;case Number:e=o===null?null:Number(o);break;case Object:case Array:try{e=JSON.parse(o)}catch{e=null}}return e}},z=(o,t)=>!xt(o,t),lt={attribute:!0,type:String,converter:O,reflect:!1,useDefault:!1,hasChanged:z};Symbol.metadata??=Symbol("metadata"),D.litPropertyMetadata??=new WeakMap;var m=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=lt){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),r=this.getPropertyDescriptor(t,s,e);r!==void 0&&Et(this.prototype,t,r)}}static getPropertyDescriptor(t,e,s){let{get:r,set:i}=St(this.prototype,t)??{get(){return this[e]},set(n){this[e]=n}};return{get:r,set(n){let l=r?.call(this);i?.call(this,n),this.requestUpdate(t,l,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??lt}static _$Ei(){if(this.hasOwnProperty(U("elementProperties")))return;let t=Pt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(U("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(U("properties"))){let e=this.properties,s=[...wt(e),...Ct(e)];for(let r of s)this.createProperty(r,e[r])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,r]of e)this.elementProperties.set(s,r)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let r=this._$Eu(e,s);r!==void 0&&this._$Eh.set(r,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let r of s)e.unshift(F(r))}else t!==void 0&&e.push(F(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return nt(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),r=this.constructor._$Eu(t,s);if(r!==void 0&&s.reflect===!0){let i=(s.converter?.toAttribute!==void 0?s.converter:O).toAttribute(e,s.type);this._$Em=t,i==null?this.removeAttribute(r):this.setAttribute(r,i),this._$Em=null}}_$AK(t,e){let s=this.constructor,r=s._$Eh.get(t);if(r!==void 0&&this._$Em!==r){let i=s.getPropertyOptions(r),n=typeof i.converter=="function"?{fromAttribute:i.converter}:i.converter?.fromAttribute!==void 0?i.converter:O;this._$Em=r;let l=n.fromAttribute(e,i.type);this[r]=l??this._$Ej?.get(r)??l,this._$Em=null}}requestUpdate(t,e,s,r=!1,i){if(t!==void 0){let n=this.constructor;if(r===!1&&(i=this[t]),s??=n.getPropertyOptions(t),!((s.hasChanged??z)(i,e)||s.useDefault&&s.reflect&&i===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:r,wrapped:i},n){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),i!==!0||n!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),r===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[r,i]of this._$Ep)this[r]=i;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[r,i]of s){let{wrapped:n}=i,l=this[r];n!==!0||this._$AL.has(r)||l===void 0||this.C(r,void 0,i,l)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};m.elementStyles=[],m.shadowRootOptions={mode:"open"},m[U("elementProperties")]=new Map,m[U("finalized")]=new Map,Ot?.({ReactiveElement:m}),(D.reactiveElementVersions??=[]).push("2.1.2");var tt=globalThis,ct=o=>o,B=tt.trustedTypes,ht=B?B.createPolicy("lit-html",{createHTML:o=>o}):void 0,$t="$lit$",_=`lit$${Math.random().toFixed(9).slice(2)}$`,_t="?"+_,Mt=`<${_t}>`,v=document,T=()=>v.createComment(""),N=o=>o===null||typeof o!="object"&&typeof o!="function",et=Array.isArray,Tt=o=>et(o)||typeof o?.[Symbol.iterator]=="function",J=`[ 	
\f\r]`,M=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,dt=/-->/g,pt=/>/g,g=RegExp(`>|${J}(?:([^\\s"'>=/]+)(${J}*=${J}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),ut=/'/g,ft=/"/g,gt=/^(?:script|style|textarea|title)$/i,st=o=>(t,...e)=>({_$litType$:o,strings:t,values:e}),I=st(1),It=st(2),Vt=st(3),A=Symbol.for("lit-noChange"),d=Symbol.for("lit-nothing"),mt=new WeakMap,y=v.createTreeWalker(v,129);function yt(o,t){if(!et(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return ht!==void 0?ht.createHTML(t):t}var Nt=(o,t)=>{let e=o.length-1,s=[],r,i=t===2?"<svg>":t===3?"<math>":"",n=M;for(let l=0;l<e;l++){let a=o[l],h,p,c=-1,f=0;for(;f<a.length&&(n.lastIndex=f,p=n.exec(a),p!==null);)f=n.lastIndex,n===M?p[1]==="!--"?n=dt:p[1]!==void 0?n=pt:p[2]!==void 0?(gt.test(p[2])&&(r=RegExp("</"+p[2],"g")),n=g):p[3]!==void 0&&(n=g):n===g?p[0]===">"?(n=r??M,c=-1):p[1]===void 0?c=-2:(c=n.lastIndex-p[2].length,h=p[1],n=p[3]===void 0?g:p[3]==='"'?ft:ut):n===ft||n===ut?n=g:n===dt||n===pt?n=M:(n=g,r=void 0);let $=n===g&&o[l+1].startsWith("/>")?" ":"";i+=n===M?a+Mt:c>=0?(s.push(h),a.slice(0,c)+$t+a.slice(c)+_+$):a+_+(c===-2?l:$)}return[yt(o,i+(o[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},H=class o{constructor({strings:t,_$litType$:e},s){let r;this.parts=[];let i=0,n=0,l=t.length-1,a=this.parts,[h,p]=Nt(t,e);if(this.el=o.createElement(h,s),y.currentNode=this.el.content,e===2||e===3){let c=this.el.content.firstChild;c.replaceWith(...c.childNodes)}for(;(r=y.nextNode())!==null&&a.length<l;){if(r.nodeType===1){if(r.hasAttributes())for(let c of r.getAttributeNames())if(c.endsWith($t)){let f=p[n++],$=r.getAttribute(c).split(_),L=/([.?@])?(.*)/.exec(f);a.push({type:1,index:i,name:L[2],strings:$,ctor:L[1]==="."?G:L[1]==="?"?Q:L[1]==="@"?X:E}),r.removeAttribute(c)}else c.startsWith(_)&&(a.push({type:6,index:i}),r.removeAttribute(c));if(gt.test(r.tagName)){let c=r.textContent.split(_),f=c.length-1;if(f>0){r.textContent=B?B.emptyScript:"";for(let $=0;$<f;$++)r.append(c[$],T()),y.nextNode(),a.push({type:2,index:++i});r.append(c[f],T())}}}else if(r.nodeType===8)if(r.data===_t)a.push({type:2,index:i});else{let c=-1;for(;(c=r.data.indexOf(_,c+1))!==-1;)a.push({type:7,index:i}),c+=_.length-1}i++}}static createElement(t,e){let s=v.createElement("template");return s.innerHTML=t,s}};function x(o,t,e=o,s){if(t===A)return t;let r=s!==void 0?e._$Co?.[s]:e._$Cl,i=N(t)?void 0:t._$litDirective$;return r?.constructor!==i&&(r?._$AO?.(!1),i===void 0?r=void 0:(r=new i(o),r._$AT(o,e,s)),s!==void 0?(e._$Co??=[])[s]=r:e._$Cl=r),r!==void 0&&(t=x(o,r._$AS(o,t.values),r,s)),t}var Z=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,r=(t?.creationScope??v).importNode(e,!0);y.currentNode=r;let i=y.nextNode(),n=0,l=0,a=s[0];for(;a!==void 0;){if(n===a.index){let h;a.type===2?h=new R(i,i.nextSibling,this,t):a.type===1?h=new a.ctor(i,a.name,a.strings,this,t):a.type===6&&(h=new Y(i,this,t)),this._$AV.push(h),a=s[++l]}n!==a?.index&&(i=y.nextNode(),n++)}return y.currentNode=v,r}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},R=class o{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,r){this.type=2,this._$AH=d,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=r,this._$Cv=r?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=x(this,t,e),N(t)?t===d||t==null||t===""?(this._$AH!==d&&this._$AR(),this._$AH=d):t!==this._$AH&&t!==A&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Tt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==d&&N(this._$AH)?this._$AA.nextSibling.data=t:this.T(v.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,r=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=H.createElement(yt(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===r)this._$AH.p(e);else{let i=new Z(r,this),n=i.u(this.options);i.p(e),this.T(n),this._$AH=i}}_$AC(t){let e=mt.get(t.strings);return e===void 0&&mt.set(t.strings,e=new H(t)),e}k(t){et(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,r=0;for(let i of t)r===e.length?e.push(s=new o(this.O(T()),this.O(T()),this,this.options)):s=e[r],s._$AI(i),r++;r<e.length&&(this._$AR(s&&s._$AB.nextSibling,r),e.length=r)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=ct(t).nextSibling;ct(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},E=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,r,i){this.type=1,this._$AH=d,this._$AN=void 0,this.element=t,this.name=e,this._$AM=r,this.options=i,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=d}_$AI(t,e=this,s,r){let i=this.strings,n=!1;if(i===void 0)t=x(this,t,e,0),n=!N(t)||t!==this._$AH&&t!==A,n&&(this._$AH=t);else{let l=t,a,h;for(t=i[0],a=0;a<i.length-1;a++)h=x(this,l[s+a],e,a),h===A&&(h=this._$AH[a]),n||=!N(h)||h!==this._$AH[a],h===d?t=d:t!==d&&(t+=(h??"")+i[a+1]),this._$AH[a]=h}n&&!r&&this.j(t)}j(t){t===d?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},G=class extends E{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===d?void 0:t}},Q=class extends E{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==d)}},X=class extends E{constructor(t,e,s,r,i){super(t,e,s,r,i),this.type=5}_$AI(t,e=this){if((t=x(this,t,e,0)??d)===A)return;let s=this._$AH,r=t===d&&s!==d||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,i=t!==d&&(s===d||r);r&&this.element.removeEventListener(this.name,this,s),i&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},Y=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){x(this,t)}};var Ht=tt.litHtmlPolyfillSupport;Ht?.(H,R),(tt.litHtmlVersions??=[]).push("3.3.3");var vt=(o,t,e)=>{let s=e?.renderBefore??t,r=s._$litPart$;if(r===void 0){let i=e?.renderBefore??null;s._$litPart$=r=new R(t.insertBefore(T(),i),i,void 0,e??{})}return r._$AI(o),r};var rt=globalThis,u=class extends m{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=vt(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return A}};u._$litElement$=!0,u.finalized=!0,rt.litElementHydrateSupport?.({LitElement:u});var Rt=rt.litElementPolyfillSupport;Rt?.({LitElement:u});(rt.litElementVersions??=[]).push("4.2.2");var V=o=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(o,t)}):customElements.define(o,t)};var kt={attribute:!0,type:String,converter:O,reflect:!1,hasChanged:z},Lt=(o=kt,t,e)=>{let{kind:s,metadata:r}=e,i=globalThis.litPropertyMetadata.get(r);if(i===void 0&&globalThis.litPropertyMetadata.set(r,i=new Map),s==="setter"&&((o=Object.create(o)).wrapped=!0),i.set(e.name,o),s==="accessor"){let{name:n}=e;return{set(l){let a=t.get.call(this);t.set.call(this,l),this.requestUpdate(n,a,o,!0,l)},init(l){return l!==void 0&&this.C(n,void 0,o,l),l}}}if(s==="setter"){let{name:n}=e;return function(l){let a=this[n];t.call(this,l),this.requestUpdate(n,a,o,!0,l)}}throw Error("Unsupported decorator location: "+s)};function k(o){return(t,e)=>typeof e=="object"?Lt(o,t,e):((s,r,i)=>{let n=r.hasOwnProperty(i);return r.constructor.createProperty(i,s),n?Object.getOwnPropertyDescriptor(r,i):void 0})(o,t,e)}var S=class extends u{constructor(){super(...arguments);this.tone="neutral"}render(){return I`<span class="chip"><slot></slot></span>`}};S.styles=P`
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
  `,b([k({reflect:!0})],S.prototype,"tone",2),S=b([V("sx-chip")],S);var w=class extends u{constructor(){super(...arguments);this.accent="none"}render(){return I`
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
    `}};w.styles=P`
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
      margin: 4px 0 8px;
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
      margin: 0;
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
  `,b([k({reflect:!0})],w.prototype,"accent",2),w=b([V("sx-result-card")],w);
