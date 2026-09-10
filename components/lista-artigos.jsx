export const Lista = ({ titulo, children }) => (
  <div className="lista-artigos">
    {titulo ? <p className="lista-artigos-titulo">{titulo}</p> : null}
    <div className="lista-artigos-itens">{children}</div>
  </div>
);

export const Artigo = ({ titulo, href, children }) => (
  <a className="lista-artigos-item" href={href}>
    <span className="lista-artigos-texto">
      <span className="lista-artigos-nome">{titulo}</span>
      {children ? <span className="lista-artigos-desc">{children}</span> : null}
    </span>
    <svg className="lista-artigos-seta" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
      <path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  </a>
);
