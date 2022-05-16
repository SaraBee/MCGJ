class Song extends HTMLElement {
  constructor() {
    super();
  }

  onmouseleave = () => {
    const el = document.querySelector(
      `album-art.art-link[data-trackid="${id}"]`
    );
    el.toggleAttribute("highlighted");
  };

  onmouseenter = () => {
    const el = document.querySelector(
      `album-art.art-link[data-trackid="${id}"]`
    );
    el.toggleAttribute("highlighted");
  };

  disconnectedCallback() {
    console.log("disconnected");
  }
}

class RoundContainer extends HTMLElement {
  constructor() {
    super();

    this.attachShadow({ mode: "open" });
  }

  connectedCallback() {
    // if (this.isConnected) {
    //   const song = this.querySelector("session-song");
    //   console.log(song.textContent);
    // }
  }
}

class AlbumArt extends HTMLAnchorElement {
  static get observedAttributes() {
    return ["highlighted"];
  }

  constructor() {
    super();
  }

  attributeChangedCallback(name, oldVal, newVal) {
    console.log({ name, oldVal, newVal });
  }
}
customElements.define("session-song", Song);
customElements.define("round-container", RoundContainer);
customElements.define("album-art", AlbumArt, { extends: "a" });
