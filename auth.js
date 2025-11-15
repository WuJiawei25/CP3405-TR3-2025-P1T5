(function(){
  const origin = window.location.origin;
  const API_BASE = (location.protocol === 'file:' || origin === 'null' || !origin) ? 'http://127.0.0.1:8000' : origin;

  function getToken(){
    return localStorage.getItem('demo_token');
  }

  function requireAuth(){
    const t = getToken();
    if(!t){
      // Redirect to sign-in if no token
      window.location.href = 'A01_signin_credentials.html';
      throw new Error('No token');
    }
    return t;
  }

  async function apiFetch(path, options={}){
    const headers = Object.assign({'Content-Type': 'application/json'}, options.headers || {});
    const token = getToken();
    if(token){ headers['Authorization'] = 'Bearer ' + token; }
    const res = await fetch(API_BASE + path, { ...options, headers });
    if(res.status === 401){
      try { console.warn('Unauthorized, redirecting to login'); } catch(_){}
      localStorage.removeItem('demo_token');
      window.location.href = 'A01_signin_credentials.html';
      throw new Error('Unauthorized');
    }
    return res;
  }

  function logout(){
    localStorage.removeItem('demo_token');
    window.location.href = 'A01_signin_credentials.html';
  }

  function formatDate(dt){
    try{
      const d = (typeof dt === 'string') ? new Date(dt) : dt;
      return d.toLocaleString();
    } catch(_){ return String(dt); }
  }

  window.Auth = { API_BASE, getToken, requireAuth, apiFetch, logout, formatDate };
})();

