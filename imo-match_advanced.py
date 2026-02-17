import { useState, useEffect, useRef } from "react";

// ============================================================
// MOCK DATA & MATCHING ENGINE
// ============================================================

const MOCK_PROPERTIES = [
  {
    id: 1, title: "Loft Haussmannien", type: "appartement", transaction: "achat",
    price: 485000, city: "Paris 11e", surface: 87, rooms: 3,
    features: ["balcon", "parking", "gardien"], score: 0,
    img: "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600&q=80",
    description: "Magnifique loft en plein cœur de Paris avec hauteurs sous plafond exceptionnelles.",
    owner: { name: "Marie Leclerc", avatar: "ML", verified: true },
    lat: 48.858, lng: 2.379
  },
  {
    id: 2, title: "Maison Contemporaine", type: "maison", transaction: "achat",
    price: 620000, city: "Bordeaux", surface: 145, rooms: 5,
    features: ["jardin", "parking", "terrasse"], score: 0,
    img: "https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=600&q=80",
    description: "Belle maison contemporaine avec grand jardin arboré et piscine.",
    owner: { name: "Thomas Bernard", avatar: "TB", verified: true },
    lat: 44.837, lng: -0.579
  },
  {
    id: 3, title: "Studio Design Marais", type: "studio", transaction: "location",
    price: 1350, city: "Paris 4e", surface: 32, rooms: 1,
    features: ["meublé", "digicode"], score: 0,
    img: "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600&q=80",
    description: "Studio entièrement rénové dans le quartier du Marais.",
    owner: { name: "Sophie Dubois", avatar: "SD", verified: false },
    lat: 48.854, lng: 2.352
  },
  {
    id: 4, title: "Appartement Vue Mer", type: "appartement", transaction: "achat",
    price: 395000, city: "Nice", surface: 72, rooms: 3,
    features: ["terrasse", "digicode", "ascenseur"], score: 0,
    img: "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=600&q=80",
    description: "Appartement avec vue imprenable sur la mer Méditerranée.",
    owner: { name: "Jean-Marc Faure", avatar: "JF", verified: true },
    lat: 43.710, lng: 7.262
  },
  {
    id: 5, title: "T3 Centre Lyon", type: "appartement", transaction: "location",
    price: 1800, city: "Lyon", surface: 68, rooms: 3,
    features: ["balcon", "parking", "cave"], score: 0,
    img: "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=600&q=80",
    description: "Bel appartement T3 en plein centre de Lyon, lumineux et rénové.",
    owner: { name: "Chloé Martin", avatar: "CM", verified: true },
    lat: 45.750, lng: 4.845
  },
  {
    id: 6, title: "Penthouse Moderne", type: "appartement", transaction: "achat",
    price: 1250000, city: "Paris 8e", surface: 210, rooms: 6,
    features: ["terrasse", "parking", "gardien", "ascenseur"], score: 0,
    img: "https://images.unsplash.com/photo-1613977257363-707ba9348227?w=600&q=80",
    description: "Penthouse d'exception avec vue panoramique sur Paris.",
    owner: { name: "Alex Morel", avatar: "AM", verified: true },
    lat: 48.874, lng: 2.308
  },
  {
    id: 7, title: "Villa Provençale", type: "maison", transaction: "achat",
    price: 780000, city: "Aix-en-Provence", surface: 200, rooms: 7,
    features: ["jardin", "parking", "piscine", "terrasse"], score: 0,
    img: "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=600&q=80",
    description: "Magnifique villa provençale avec piscine et oliviers centenaires.",
    owner: { name: "Isabelle Roux", avatar: "IR", verified: true },
    lat: 43.529, lng: 5.447
  },
  {
    id: 8, title: "Loft Industriel", type: "appartement", transaction: "location",
    price: 2400, city: "Paris 10e", surface: 95, rooms: 2,
    features: ["parking", "balcon"], score: 0,
    img: "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=600&q=80",
    description: "Loft à l'esprit industriel chic avec très hauts plafonds.",
    owner: { name: "Pierre Blanc", avatar: "PB", verified: false },
    lat: 48.876, lng: 2.361
  },
];

const MOCK_BUYERS = [
  { id: 1, name: "Emma Rousseau", avatar: "ER", transaction: "achat", type: "appartement", budget: [400000, 550000], city: "Paris", surface: 70, rooms: 3, features: ["balcon"], score: 0 },
  { id: 2, name: "Lucas Petit", avatar: "LP", transaction: "location", type: "studio", budget: [900, 1400], city: "Paris", surface: 25, rooms: 1, features: ["meublé"], score: 0 },
  { id: 3, name: "Camille Noel", avatar: "CN", transaction: "achat", type: "maison", budget: [500000, 700000], city: "Bordeaux", surface: 120, rooms: 4, features: ["jardin"], score: 0 },
  { id: 4, name: "Hugo Martin", avatar: "HM", transaction: "location", type: "appartement", budget: [1500, 2000], city: "Lyon", surface: 60, rooms: 3, features: ["balcon"], score: 0 },
];

function computeMatchScore(buyer, property) {
  let score = 0;
  if (buyer.transaction === property.transaction) score += 30;
  if (buyer.type === property.type) score += 20;
  const budgetMid = (buyer.budget[0] + buyer.budget[1]) / 2;
  if (property.price >= buyer.budget[0] && property.price <= buyer.budget[1]) score += 25;
  else score += Math.max(0, 10 - Math.abs(property.price - budgetMid) / budgetMid * 10);
  if (property.surface >= buyer.surface) score += 10;
  if (property.rooms >= buyer.rooms) score += 10;
  if (buyer.city && property.city.toLowerCase().includes(buyer.city.toLowerCase())) score += 5;
  return Math.min(100, Math.round(score));
}

// ============================================================
// ICONS (inline SVG)
// ============================================================
const Icon = {
  Home: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>,
  Heart: ({filled}) => <svg viewBox="0 0 24 24" fill={filled ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>,
  Chat: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>,
  User: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>,
  Plus: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>,
  Search: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>,
  Bell: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>,
  MapPin: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>,
  Star: () => <svg viewBox="0 0 24 24" fill="currentColor" stroke="none" className="w-4 h-4"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>,
  Send: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>,
  X: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
  ChevronRight: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><polyline points="9 18 15 12 9 6"/></svg>,
  LogOut: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>,
  Check: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="w-4 h-4"><polyline points="20 6 9 17 4 12"/></svg>,
  Zap: () => <svg viewBox="0 0 24 24" fill="currentColor" stroke="none" className="w-4 h-4"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>,
  Filter: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>,
  ArrowRight: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>,
};

// ============================================================
// DESIGN SYSTEM
// ============================================================
const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;0,9..144,800;1,9..144,400&family=DM+Sans:wght@300;400;500;600&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  
  :root {
    --primary: #E8633A;
    --primary-dark: #C94E28;
    --primary-light: #FDEEE8;
    --accent: #2D3250;
    --accent-light: #424769;
    --gold: #F0A500;
    --surface: #FAFAF8;
    --surface-2: #F3F2EF;
    --border: #E5E3DF;
    --text: #1A1917;
    --text-2: #6B6860;
    --text-3: #9B9A96;
    --success: #2CA05A;
    --radius: 16px;
    --radius-sm: 10px;
    --shadow: 0 4px 24px rgba(0,0,0,0.08);
    --shadow-lg: 0 12px 48px rgba(0,0,0,0.14);
    --font-display: 'Fraunces', Georgia, serif;
    --font-body: 'DM Sans', -apple-system, sans-serif;
  }

  html, body { height: 100%; font-family: var(--font-body); background: var(--surface); color: var(--text); }

  .app-layout { display: flex; height: 100vh; overflow: hidden; }
  
  /* Sidebar */
  .sidebar {
    width: 72px; background: var(--accent); display: flex; flex-direction: column;
    align-items: center; padding: 20px 0; gap: 8px; flex-shrink: 0; transition: width 0.3s ease;
    position: relative; z-index: 100;
  }
  .sidebar.expanded { width: 220px; }
  .sidebar-logo { 
    font-family: var(--font-display); font-weight: 800; font-size: 22px; color: white;
    padding: 12px; margin-bottom: 8px; line-height: 1; letter-spacing: -0.5px; cursor: pointer;
    white-space: nowrap; overflow: hidden;
  }
  .sidebar-logo span { color: var(--primary); }
  .nav-item {
    width: calc(100% - 16px); display: flex; align-items: center; gap: 12px;
    padding: 12px 16px; border-radius: var(--radius-sm); cursor: pointer; 
    transition: all 0.2s; color: rgba(255,255,255,0.6); text-decoration: none;
    white-space: nowrap; overflow: hidden; font-size: 14px; font-weight: 500;
  }
  .nav-item:hover { background: rgba(255,255,255,0.08); color: white; }
  .nav-item.active { background: var(--primary); color: white; }
  .nav-item svg { flex-shrink: 0; width: 20px; height: 20px; }
  .nav-spacer { flex: 1; }
  .nav-badge { background: var(--primary); color: white; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 20px; margin-left: auto; }

  /* Main content */
  .main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
  .topbar {
    height: 64px; background: white; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; padding: 0 28px; gap: 16px; flex-shrink: 0;
  }
  .topbar-title { font-family: var(--font-display); font-size: 20px; font-weight: 600; flex: 1; }
  .topbar-actions { display: flex; align-items: center; gap: 12px; }
  .icon-btn { 
    width: 38px; height: 38px; border-radius: 50%; border: 1px solid var(--border);
    background: white; display: flex; align-items: center; justify-content: center;
    cursor: pointer; color: var(--text-2); transition: all 0.2s; position: relative;
  }
  .icon-btn:hover { background: var(--surface-2); color: var(--text); }
  .icon-btn .badge { 
    position: absolute; top: -3px; right: -3px; width: 16px; height: 16px;
    background: var(--primary); border-radius: 50%; border: 2px solid white;
    font-size: 9px; color: white; font-weight: 700; display: flex; align-items: center; justify-content: center;
  }
  .avatar-btn { 
    width: 38px; height: 38px; border-radius: 50%; background: var(--primary);
    color: white; font-size: 13px; font-weight: 700; display: flex; align-items: center; justify-content: center;
    cursor: pointer; font-family: var(--font-body); border: 2px solid transparent; transition: all 0.2s;
  }
  .avatar-btn:hover { border-color: var(--primary); background: var(--primary-dark); }
  .content { flex: 1; overflow-y: auto; padding: 28px; }

  /* Cards */
  .property-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
  .property-card {
    background: white; border-radius: var(--radius); overflow: hidden; 
    border: 1px solid var(--border); transition: all 0.3s; cursor: pointer;
    animation: fadeUp 0.4s ease forwards; opacity: 0;
  }
  .property-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); border-color: transparent; }
  .card-img { width: 100%; height: 200px; object-fit: cover; display: block; }
  .card-img-placeholder { width: 100%; height: 200px; background: var(--surface-2); display: flex; align-items: center; justify-content: center; font-size: 40px; }
  .card-body { padding: 18px; }
  .card-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 8px; }
  .card-title { font-family: var(--font-display); font-size: 17px; font-weight: 600; line-height: 1.3; }
  .card-price { font-size: 18px; font-weight: 700; color: var(--primary); white-space: nowrap; margin-left: 8px; }
  .card-location { display: flex; align-items: center; gap: 4px; color: var(--text-2); font-size: 13px; margin-bottom: 12px; }
  .card-meta { display: flex; gap: 12px; font-size: 13px; color: var(--text-2); margin-bottom: 14px; }
  .card-meta span { display: flex; align-items: center; gap: 4px; }
  .card-features { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }
  .feature-chip { 
    background: var(--surface-2); border-radius: 20px; padding: 4px 10px; 
    font-size: 12px; color: var(--text-2); text-transform: capitalize;
  }
  .card-footer { display: flex; align-items: center; gap: 8px; padding-top: 14px; border-top: 1px solid var(--border); }
  .match-badge { 
    display: flex; align-items: center; gap: 4px; background: var(--primary-light);
    color: var(--primary); font-size: 12px; font-weight: 700; padding: 4px 10px;
    border-radius: 20px; margin-right: auto;
  }
  .match-badge.high { background: #e8f5e9; color: var(--success); }
  .match-badge.medium { background: #fff8e1; color: #F0A500; }
  .btn { 
    display: inline-flex; align-items: center; justify-content: center; gap: 8px;
    padding: 10px 18px; border-radius: var(--radius-sm); font-size: 14px; font-weight: 600;
    cursor: pointer; border: none; font-family: var(--font-body); transition: all 0.2s; white-space: nowrap;
  }
  .btn-primary { background: var(--primary); color: white; }
  .btn-primary:hover { background: var(--primary-dark); transform: translateY(-1px); }
  .btn-secondary { background: var(--surface-2); color: var(--text); border: 1px solid var(--border); }
  .btn-secondary:hover { background: var(--border); }
  .btn-ghost { background: transparent; color: var(--text-2); }
  .btn-ghost:hover { color: var(--text); background: var(--surface-2); }
  .btn-sm { padding: 7px 14px; font-size: 13px; }
  .btn-icon { width: 36px; height: 36px; padding: 0; border-radius: 50%; }
  .btn-fav { 
    width: 36px; height: 36px; border-radius: 50%; border: 1px solid var(--border);
    background: white; display: flex; align-items: center; justify-content: center;
    cursor: pointer; color: var(--text-3); transition: all 0.2s;
  }
  .btn-fav:hover, .btn-fav.active { color: var(--primary); border-color: var(--primary); background: var(--primary-light); }

  /* Tags */
  .tag { 
    display: inline-flex; align-items: center; gap: 4px; padding: 4px 12px;
    border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
  }
  .tag-achat { background: #E8F5E9; color: #2CA05A; }
  .tag-location { background: #E3F2FD; color: #1976D2; }
  .tag-maison { background: #FFF3E0; color: #E65100; }
  .tag-appartement { background: #F3E5F5; color: #7B1FA2; }
  .tag-studio { background: #E0F7FA; color: #00838F; }

  /* Score ring */
  .score-ring { position: relative; display: inline-flex; align-items: center; justify-content: center; }
  .score-ring svg { transform: rotate(-90deg); }
  .score-ring .score-text { 
    position: absolute; font-size: 11px; font-weight: 800; color: var(--primary);
    display: flex; align-items: center; justify-content: center; flex-direction: column; line-height: 1;
  }

  /* Chat */
  .chat-layout { display: flex; height: 100%; gap: 0; background: white; border-radius: var(--radius); overflow: hidden; border: 1px solid var(--border); }
  .chat-list { width: 280px; border-right: 1px solid var(--border); display: flex; flex-direction: column; flex-shrink: 0; }
  .chat-list-header { padding: 20px; border-bottom: 1px solid var(--border); font-family: var(--font-display); font-size: 18px; font-weight: 600; }
  .chat-list-items { flex: 1; overflow-y: auto; }
  .chat-item { 
    display: flex; align-items: center; gap: 12px; padding: 14px 16px; cursor: pointer;
    transition: background 0.15s; border-bottom: 1px solid var(--surface-2);
  }
  .chat-item:hover { background: var(--surface); }
  .chat-item.active { background: var(--primary-light); }
  .chat-avatar { 
    width: 44px; height: 44px; border-radius: 50%; background: var(--accent);
    color: white; font-size: 14px; font-weight: 700; display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; font-family: var(--font-body);
  }
  .chat-item-info { flex: 1; min-width: 0; }
  .chat-item-name { font-weight: 600; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .chat-item-preview { font-size: 12px; color: var(--text-2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px; }
  .chat-item-time { font-size: 11px; color: var(--text-3); flex-shrink: 0; }
  .chat-main { flex: 1; display: flex; flex-direction: column; }
  .chat-header { padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 12px; }
  .chat-messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; background: var(--surface); }
  .message { display: flex; gap: 8px; max-width: 70%; }
  .message.mine { align-self: flex-end; flex-direction: row-reverse; }
  .message-avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--surface-2); display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex-shrink: 0; color: var(--text-2); }
  .message.mine .message-avatar { background: var(--primary); color: white; }
  .message-bubble { 
    background: white; border: 1px solid var(--border); border-radius: 18px; border-bottom-left-radius: 4px;
    padding: 10px 14px; font-size: 14px; line-height: 1.5;
  }
  .message.mine .message-bubble { 
    background: var(--primary); color: white; border: none; 
    border-radius: 18px; border-bottom-right-radius: 4px;
  }
  .message-time { font-size: 11px; color: var(--text-3); margin-top: 4px; display: block; }
  .message.mine .message-time { text-align: right; color: rgba(255,255,255,0.7); }
  .chat-input { padding: 16px 20px; border-top: 1px solid var(--border); display: flex; gap: 10px; background: white; }
  .chat-input input { 
    flex: 1; border: 1px solid var(--border); border-radius: 24px; padding: 10px 18px;
    font-size: 14px; outline: none; font-family: var(--font-body); background: var(--surface);
    transition: border-color 0.2s;
  }
  .chat-input input:focus { border-color: var(--primary); background: white; }

  /* Auth */
  .auth-container { 
    min-height: 100vh; display: flex; background: var(--accent);
    position: relative; overflow: hidden;
  }
  .auth-left { 
    flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 60px;
    position: relative; z-index: 1;
  }
  .auth-right { 
    flex: 1; background: white; display: flex; flex-direction: column; justify-content: center;
    align-items: center; padding: 60px; position: relative;
  }
  .auth-card { width: 100%; max-width: 420px; }
  .auth-logo { font-family: var(--font-display); font-size: 48px; font-weight: 800; color: white; line-height: 1; margin-bottom: 20px; }
  .auth-logo span { color: var(--primary); }
  .auth-tagline { font-size: 18px; color: rgba(255,255,255,0.7); font-weight: 300; line-height: 1.6; max-width: 360px; }
  .auth-features { margin-top: 48px; display: flex; flex-direction: column; gap: 16px; }
  .auth-feature { display: flex; align-items: center; gap: 14px; color: rgba(255,255,255,0.85); font-size: 15px; }
  .auth-feature-icon { width: 36px; height: 36px; border-radius: 10px; background: rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: var(--primary); }
  .form-group { margin-bottom: 18px; }
  .form-label { display: block; font-size: 13px; font-weight: 600; color: var(--text-2); margin-bottom: 6px; letter-spacing: 0.3px; }
  .form-input { 
    width: 100%; padding: 12px 16px; border: 1.5px solid var(--border); border-radius: var(--radius-sm);
    font-size: 15px; outline: none; font-family: var(--font-body); color: var(--text);
    transition: border-color 0.2s, box-shadow 0.2s; background: var(--surface);
  }
  .form-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(232,99,58,0.12); background: white; }
  .form-select { appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236B6860' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 12px center; background-size: 16px; }
  .auth-title { font-family: var(--font-display); font-size: 32px; font-weight: 700; margin-bottom: 8px; color: var(--text); }
  .auth-subtitle { color: var(--text-2); font-size: 15px; margin-bottom: 32px; }
  .auth-tabs { display: flex; background: var(--surface-2); border-radius: var(--radius-sm); padding: 4px; margin-bottom: 28px; gap: 4px; }
  .auth-tab { 
    flex: 1; padding: 8px; border-radius: 8px; text-align: center; cursor: pointer;
    font-size: 14px; font-weight: 600; color: var(--text-2); transition: all 0.2s;
  }
  .auth-tab.active { background: white; color: var(--text); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
  .auth-link { text-align: center; margin-top: 20px; font-size: 14px; color: var(--text-2); }
  .auth-link button { background: none; border: none; color: var(--primary); font-weight: 600; cursor: pointer; font-family: var(--font-body); font-size: 14px; }
  .orb { position: absolute; border-radius: 50%; background: radial-gradient(circle, rgba(232,99,58,0.25) 0%, transparent 70%); pointer-events: none; }

  /* Modal */
  .modal-overlay { 
    position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1000; 
    display: flex; align-items: center; justify-content: center; padding: 20px;
    backdrop-filter: blur(4px); animation: fadeIn 0.15s ease;
  }
  .modal { 
    background: white; border-radius: 20px; max-width: 640px; width: 100%; max-height: 85vh; overflow-y: auto;
    animation: scaleIn 0.2s ease; box-shadow: var(--shadow-lg);
  }
  .modal-header { padding: 24px 28px 0; display: flex; align-items: flex-start; justify-content: space-between; }
  .modal-title { font-family: var(--font-display); font-size: 24px; font-weight: 700; }
  .modal-body { padding: 24px 28px; }
  .modal-footer { padding: 0 28px 24px; display: flex; gap: 10px; justify-content: flex-end; }

  /* Dashboard stats */
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; margin-bottom: 28px; }
  .stat-card { 
    background: white; border-radius: var(--radius); padding: 22px; border: 1px solid var(--border);
    display: flex; flex-direction: column; gap: 8px;
  }
  .stat-number { font-family: var(--font-display); font-size: 36px; font-weight: 800; color: var(--accent); line-height: 1; }
  .stat-label { font-size: 13px; color: var(--text-2); font-weight: 500; }
  .stat-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 4px; }
  .stat-icon.orange { background: var(--primary-light); color: var(--primary); }
  .stat-icon.blue { background: #E3F2FD; color: #1976D2; }
  .stat-icon.green { background: #E8F5E9; color: #2CA05A; }
  .stat-icon.purple { background: #F3E5F5; color: #7B1FA2; }

  /* Profile section */
  .profile-header { 
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%);
    border-radius: var(--radius); padding: 32px; color: white; margin-bottom: 24px;
    position: relative; overflow: hidden;
  }
  .profile-avatar-lg {
    width: 80px; height: 80px; border-radius: 50%; background: var(--primary);
    color: white; font-size: 28px; font-weight: 700; display: flex; align-items: center; justify-content: center;
    border: 3px solid rgba(255,255,255,0.3); margin-bottom: 16px;
  }
  .profile-name { font-family: var(--font-display); font-size: 28px; font-weight: 700; margin-bottom: 4px; }
  .profile-role { color: rgba(255,255,255,0.7); font-size: 15px; }
  .section-title { font-family: var(--font-display); font-size: 22px; font-weight: 700; margin-bottom: 20px; }
  .section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }

  /* Hero area */
  .hero { 
    background: linear-gradient(135deg, var(--accent) 0%, #1A1B35 100%);
    padding: 40px 28px; color: white; position: relative; overflow: hidden; border-radius: var(--radius); margin-bottom: 28px;
  }
  .hero h1 { font-family: var(--font-display); font-size: 36px; font-weight: 800; margin-bottom: 10px; line-height: 1.2; }
  .hero h1 span { color: var(--primary); }
  .hero p { color: rgba(255,255,255,0.7); font-size: 16px; max-width: 500px; }
  .hero-orb { position: absolute; right: -40px; top: -40px; width: 280px; height: 280px; border-radius: 50%; background: radial-gradient(circle, rgba(232,99,58,0.2) 0%, transparent 70%); }
  .hero-orb-2 { position: absolute; right: 60px; bottom: -60px; width: 180px; height: 180px; border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%); }

  /* Filters */
  .filters { 
    background: white; border-radius: var(--radius); border: 1px solid var(--border); 
    padding: 20px; margin-bottom: 24px; display: flex; flex-wrap: wrap; gap: 14px; align-items: flex-end;
  }
  .filter-group { display: flex; flex-direction: column; gap: 6px; min-width: 140px; flex: 1; }
  .filter-label { font-size: 12px; font-weight: 600; color: var(--text-2); letter-spacing: 0.4px; text-transform: uppercase; }

  /* Animations */
  @keyframes fadeUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
  @keyframes scaleIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
  @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
  
  .property-card:nth-child(1) { animation-delay: 0.05s; }
  .property-card:nth-child(2) { animation-delay: 0.1s; }
  .property-card:nth-child(3) { animation-delay: 0.15s; }
  .property-card:nth-child(4) { animation-delay: 0.2s; }
  .property-card:nth-child(5) { animation-delay: 0.25s; }
  .property-card:nth-child(6) { animation-delay: 0.3s; }
  .property-card:nth-child(7) { animation-delay: 0.35s; }
  .property-card:nth-child(8) { animation-delay: 0.4s; }

  /* Notification */
  .notification-toast {
    position: fixed; bottom: 24px; right: 24px; background: var(--accent); color: white;
    padding: 14px 20px; border-radius: var(--radius-sm); font-size: 14px; font-weight: 500;
    box-shadow: var(--shadow-lg); z-index: 9999; display: flex; align-items: center; gap: 10px;
    animation: slideInRight 0.3s ease, fadeOut 0.3s ease 2.7s forwards;
    max-width: 320px;
  }
  @keyframes slideInRight { from { transform: translateX(120%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
  @keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }

  /* Premium badge */
  .premium-badge { 
    background: linear-gradient(135deg, #FFD700, #FFA500); color: #1A1917;
    font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 20px; letter-spacing: 0.5px;
    text-transform: uppercase;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: var(--text-3); }

  /* Tabs */
  .tabs { display: flex; gap: 4px; background: var(--surface-2); border-radius: var(--radius-sm); padding: 4px; margin-bottom: 24px; width: fit-content; }
  .tab { padding: 8px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; color: var(--text-2); transition: all 0.2s; }
  .tab.active { background: white; color: var(--text); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }

  /* Progress bar */
  .progress-bar { height: 6px; background: var(--surface-2); border-radius: 3px; overflow: hidden; }
  .progress-fill { height: 100%; border-radius: 3px; transition: width 0.8s ease; }

  /* Empty state */
  .empty-state { text-align: center; padding: 60px 20px; color: var(--text-2); }
  .empty-state h3 { font-family: var(--font-display); font-size: 22px; color: var(--text); margin: 16px 0 8px; }

  /* Search bar */
  .search-bar { 
    display: flex; align-items: center; gap: 10px; background: var(--surface-2); border: 1.5px solid var(--border);
    border-radius: 24px; padding: 10px 18px; color: var(--text-2); cursor: text; transition: all 0.2s;
    flex: 1; max-width: 320px; font-size: 14px;
  }

  @media (max-width: 768px) {
    .sidebar { width: 60px; }
    .sidebar-logo { font-size: 16px; }
    .auth-left { display: none; }
    .auth-right { flex: 1; }
    .property-grid { grid-template-columns: 1fr; }
    .chat-list { width: 220px; }
  }
`;

// ============================================================
// SCORE RING COMPONENT
// ============================================================
function ScoreRing({ score, size = 44 }) {
  const r = (size - 6) / 2;
  const circ = 2 * Math.PI * r;
  const color = score >= 75 ? "#2CA05A" : score >= 50 ? "#F0A500" : "#E8633A";
  return (
    <div className="score-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#F3F2EF" strokeWidth="5"/>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="5"
          strokeDasharray={circ} strokeDashoffset={circ * (1 - score/100)} strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 1s ease" }}/>
      </svg>
      <div className="score-text" style={{ color }}>
        <span style={{ fontSize: size < 40 ? 9 : 11 }}>{score}%</span>
      </div>
    </div>
  );
}

// ============================================================
// PROPERTY CARD
// ============================================================
function PropertyCard({ property, onContact, buyer, onClick }) {
  const [fav, setFav] = useState(false);
  const score = buyer ? computeMatchScore(buyer, property) : 0;
  const scoreClass = score >= 75 ? "high" : score >= 50 ? "medium" : "";
  const price = property.transaction === "location"
    ? `${property.price.toLocaleString()}€/mois`
    : `${property.price.toLocaleString()}€`;

  return (
    <div className="property-card" onClick={() => onClick && onClick(property)}>
      <div style={{ position: "relative" }}>
        <img src={property.img} alt={property.title} className="card-img"
          onError={e => { e.target.style.display='none'; e.target.nextSibling.style.display='flex'; }}/>
        <div className="card-img-placeholder" style={{ display: "none" }}>🏠</div>
        <div style={{ position: "absolute", top: 12, left: 12, display: "flex", gap: 6 }}>
          <span className={`tag tag-${property.transaction}`}>{property.transaction}</span>
          <span className={`tag tag-${property.type}`}>{property.type}</span>
        </div>
        <button className={`btn-fav ${fav ? "active" : ""}`}
          style={{ position: "absolute", top: 12, right: 12 }}
          onClick={e => { e.stopPropagation(); setFav(!fav); }}>
          <Icon.Heart filled={fav} />
        </button>
        {property.owner.verified && (
          <div style={{ position: "absolute", bottom: 12, right: 12, background: "white", borderRadius: 20, padding: "4px 10px", fontSize: 12, fontWeight: 600, display: "flex", alignItems: "center", gap: 4, color: "#2CA05A" }}>
            <Icon.Check /><span>Vérifié</span>
          </div>
        )}
      </div>
      <div className="card-body">
        <div className="card-header">
          <h3 className="card-title">{property.title}</h3>
          <span className="card-price">{price}</span>
        </div>
        <div className="card-location">
          <Icon.MapPin /><span>{property.city}</span>
        </div>
        <div className="card-meta">
          <span>📐 {property.surface}m²</span>
          <span>🏠 {property.rooms} pièces</span>
        </div>
        <div className="card-features">
          {property.features.map(f => <span key={f} className="feature-chip">{f}</span>)}
        </div>
        <div className="card-footer">
          {buyer ? (
            <div className={`match-badge ${scoreClass}`}>
              <Icon.Zap />
              Match {score}%
            </div>
          ) : (
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginRight: "auto" }}>
              <div className="chat-avatar" style={{ width: 28, height: 28, fontSize: 11 }}>{property.owner.avatar}</div>
              <span style={{ fontSize: 13, color: "var(--text-2)" }}>{property.owner.name}</span>
            </div>
          )}
          {buyer && (
            <button className="btn btn-secondary btn-sm" onClick={e => { e.stopPropagation(); onContact && onContact(property); }}>
              <Icon.Chat />
            </button>
          )}
          <button className="btn btn-primary btn-sm" onClick={e => { e.stopPropagation(); onClick && onClick(property); }}>
            Voir
          </button>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// PROPERTY MODAL
// ============================================================
function PropertyModal({ property, onClose, onContact, buyer }) {
  const score = buyer ? computeMatchScore(buyer, property) : 0;
  const price = property.transaction === "location"
    ? `${property.price.toLocaleString()}€/mois`
    : `${property.price.toLocaleString()}€`;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 700 }}>
        <div style={{ position: "relative" }}>
          <img src={property.img} alt={property.title} style={{ width: "100%", height: 260, objectFit: "cover", borderRadius: "20px 20px 0 0", display: "block" }}
            onError={e => e.target.style.background = "#F3F2EF"}/>
          <button className="icon-btn" style={{ position: "absolute", top: 16, right: 16, background: "white" }} onClick={onClose}>
            <Icon.X />
          </button>
        </div>
        <div className="modal-body">
          <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 12 }}>
            <div>
              <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
                <span className={`tag tag-${property.transaction}`}>{property.transaction}</span>
                <span className={`tag tag-${property.type}`}>{property.type}</span>
              </div>
              <h2 style={{ fontFamily: "var(--font-display)", fontSize: 26, fontWeight: 700, marginBottom: 6 }}>{property.title}</h2>
              <div className="card-location"><Icon.MapPin /><span style={{ fontSize: 15 }}>{property.city}</span></div>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontFamily: "var(--font-display)", fontSize: 28, fontWeight: 800, color: "var(--primary)" }}>{price}</div>
              {buyer && <div style={{ marginTop: 8 }}><ScoreRing score={score} size={56} /></div>}
            </div>
          </div>

          <p style={{ color: "var(--text-2)", fontSize: 15, lineHeight: 1.7, marginBottom: 20 }}>{property.description}</p>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 20 }}>
            {[["📐", "Surface", `${property.surface}m²`], ["🏠", "Pièces", property.rooms], ["💰", "Prix/m²", `${Math.round(property.price/property.surface).toLocaleString()}€`]].map(([emoji, label, val]) => (
              <div key={label} style={{ background: "var(--surface-2)", borderRadius: "var(--radius-sm)", padding: 16, textAlign: "center" }}>
                <div style={{ fontSize: 24, marginBottom: 4 }}>{emoji}</div>
                <div style={{ fontSize: 12, color: "var(--text-2)", fontWeight: 600 }}>{label}</div>
                <div style={{ fontSize: 16, fontWeight: 700 }}>{val}</div>
              </div>
            ))}
          </div>

          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-2)", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.4px" }}>Équipements</div>
            <div className="card-features">
              {property.features.map(f => <span key={f} className="feature-chip" style={{ background: "var(--primary-light)", color: "var(--primary)" }}>{f}</span>)}
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 12, background: "var(--surface)", borderRadius: "var(--radius-sm)", padding: 14 }}>
            <div className="chat-avatar">{property.owner.avatar}</div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 15 }}>{property.owner.name}</div>
              <div style={{ fontSize: 12, color: "var(--text-2)" }}>Propriétaire {property.owner.verified ? "✅ vérifié" : ""}</div>
            </div>
            <button className="btn btn-primary" style={{ marginLeft: "auto" }} onClick={() => onContact && onContact(property)}>
              <Icon.Chat /> Contacter
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// AUTH SCREEN
// ============================================================
function AuthScreen({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [role, setRole] = useState("buyer");
  const [form, setForm] = useState({ name: "", email: "", password: "" });

  const handleSubmit = () => {
    if (!form.email) return;
    onLogin({ name: form.name || "Utilisateur", email: form.email, role, initials: (form.name || "U").slice(0, 2).toUpperCase() });
  };

  return (
    <div className="auth-container">
      <style>{styles}</style>
      <div className="orb" style={{ width: 600, height: 600, top: -200, left: -200 }} />
      <div className="orb" style={{ width: 300, height: 300, bottom: -100, left: 200 }} />

      <div className="auth-left">
        <div className="auth-logo">imo<span>Match</span></div>
        <p className="auth-tagline">
          La première plateforme immobilière basée sur le matching intelligent. Trouvez votre bien idéal en quelques clics.
        </p>
        <div className="auth-features">
          {[["🎯", "Matching IA", "Algorithme de correspondance avancé"],
            ["⚡", "Instantané", "Résultats en temps réel"],
            ["🔒", "Sécurisé", "Données chiffrées et protégées"],
            ["💬", "Messagerie", "Communication directe entre parties"]].map(([icon, title, desc]) => (
            <div key={title} className="auth-feature">
              <div className="auth-feature-icon">{icon}</div>
              <div><strong>{title}</strong> — {desc}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-card">
          <h1 className="auth-title">{mode === "login" ? "Bon retour 👋" : "Créer un compte"}</h1>
          <p className="auth-subtitle">{mode === "login" ? "Connectez-vous à votre espace" : "Rejoignez des milliers d'utilisateurs"}</p>

          <div className="auth-tabs">
            <div className={`auth-tab ${role === "buyer" ? "active" : ""}`} onClick={() => setRole("buyer")}>🔍 Chercheur</div>
            <div className={`auth-tab ${role === "seller" ? "active" : ""}`} onClick={() => setRole("seller")}>🏠 Propriétaire</div>
          </div>

          {mode === "register" && (
            <div className="form-group">
              <label className="form-label">Nom complet</label>
              <input className="form-input" placeholder="Jean Dupont" value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
            </div>
          )}
          <div className="form-group">
            <label className="form-label">Adresse email</label>
            <input className="form-input" type="email" placeholder="jean@exemple.fr" value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
          </div>
          <div className="form-group">
            <label className="form-label">Mot de passe</label>
            <input className="form-input" type="password" placeholder="••••••••" value={form.password} onChange={e => setForm({...form, password: e.target.value})} />
          </div>

          <button className="btn btn-primary" style={{ width: "100%", padding: "14px", fontSize: 16, marginTop: 8 }} onClick={handleSubmit}>
            {mode === "login" ? "Se connecter" : "Créer mon compte"}
            <Icon.ArrowRight />
          </button>

          <div className="auth-link">
            {mode === "login" ? "Pas encore de compte ? " : "Déjà un compte ? "}
            <button onClick={() => setMode(mode === "login" ? "register" : "login")}>
              {mode === "login" ? "S'inscrire" : "Se connecter"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// DASHBOARD VIEW
// ============================================================
function DashboardView({ user, properties, setActiveView }) {
  const buyer = { transaction: "achat", type: "appartement", budget: [350000, 600000], city: "Paris", surface: 60, rooms: 2, features: ["balcon"] };
  const topMatches = properties
    .map(p => ({ ...p, score: computeMatchScore(buyer, p) }))
    .sort((a, b) => b.score - a.score).slice(0, 3);
  const [selected, setSelected] = useState(null);

  return (
    <div className="content">
      <div className="hero">
        <div className="hero-orb" />
        <div className="hero-orb-2" />
        <div style={{ position: "relative", zIndex: 1 }}>
          <h1>Bienvenue, <span>{user.name.split(" ")[0]}</span> !</h1>
          <p>Votre tableau de bord imoMatch — {topMatches[0]?.score}% de compatibilité sur votre meilleur match du jour.</p>
          <div style={{ marginTop: 20, display: "flex", gap: 10 }}>
            <button className="btn btn-primary" onClick={() => setActiveView("search")}>
              <Icon.Search /> Rechercher
            </button>
            {user.role === "seller" && (
              <button className="btn btn-secondary" style={{ background: "rgba(255,255,255,0.15)", color: "white", border: "1px solid rgba(255,255,255,0.2)" }}>
                <Icon.Plus /> Publier un bien
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="stats-grid">
        {[
          { label: "Biens matchés", value: 24, icon: "🎯", cls: "orange" },
          { label: "Messages reçus", value: 3, icon: "💬", cls: "blue" },
          { label: "Favoris", value: 7, icon: "❤️", cls: "green" },
          { label: "Score moyen", value: "72%", icon: "⭐", cls: "purple" },
        ].map(s => (
          <div key={s.label} className="stat-card">
            <div className={`stat-icon ${s.cls}`}><span style={{ fontSize: 20 }}>{s.icon}</span></div>
            <div className="stat-number">{s.value}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="section-header">
        <h2 className="section-title" style={{ marginBottom: 0 }}>Meilleurs matchs du jour</h2>
        <button className="btn btn-ghost btn-sm" onClick={() => setActiveView("search")}>Voir tout <Icon.ChevronRight /></button>
      </div>
      <div className="property-grid">
        {topMatches.map(p => (
          <PropertyCard key={p.id} property={p} buyer={buyer} onClick={setSelected} />
        ))}
      </div>
      {selected && <PropertyModal property={selected} onClose={() => setSelected(null)} buyer={buyer} onContact={() => { setSelected(null); setActiveView("messages"); }} />}
    </div>
  );
}

// ============================================================
// SEARCH VIEW
// ============================================================
function SearchView({ properties, user }) {
  const [filters, setFilters] = useState({ transaction: "", type: "", city: "", priceMax: "", surfaceMin: "" });
  const [selected, setSelected] = useState(null);
  const [notification, setNotification] = useState(null);
  const buyer = { transaction: "achat", type: "appartement", budget: [350000, 600000], city: "Paris", surface: 60, rooms: 2, features: ["balcon"] };

  const filtered = properties.filter(p => {
    if (filters.transaction && p.transaction !== filters.transaction) return false;
    if (filters.type && p.type !== filters.type) return false;
    if (filters.city && !p.city.toLowerCase().includes(filters.city.toLowerCase())) return false;
    if (filters.priceMax && p.price > parseInt(filters.priceMax)) return false;
    if (filters.surfaceMin && p.surface < parseInt(filters.surfaceMin)) return false;
    return true;
  }).map(p => ({ ...p, score: computeMatchScore(buyer, p) })).sort((a, b) => b.score - a.score);

  const handleContact = (property) => {
    setSelected(null);
    setNotification(`✉️ Message envoyé à ${property.owner.name} !`);
    setTimeout(() => setNotification(null), 3000);
  };

  return (
    <div className="content">
      <div className="section-header">
        <h2 className="section-title" style={{ marginBottom: 0 }}>Rechercher un bien</h2>
        <div className="search-bar">
          <Icon.Search />
          <span>Ville, quartier...</span>
        </div>
      </div>

      <div className="filters">
        {[
          { label: "Transaction", key: "transaction", options: [["", "Tout"], ["achat", "Achat"], ["location", "Location"]] },
          { label: "Type", key: "type", options: [["", "Tout"], ["appartement", "Appartement"], ["maison", "Maison"], ["studio", "Studio"]] },
        ].map(f => (
          <div key={f.key} className="filter-group">
            <label className="filter-label"><Icon.Filter /> {f.label}</label>
            <select className="form-input form-select form-select" value={filters[f.key]}
              onChange={e => setFilters({...filters, [f.key]: e.target.value})}
              style={{ padding: "9px 36px 9px 14px", fontSize: 14 }}>
              {f.options.map(([val, label]) => <option key={val} value={val}>{label}</option>)}
            </select>
          </div>
        ))}
        <div className="filter-group">
          <label className="filter-label">Ville</label>
          <input className="form-input" placeholder="Paris, Lyon..." value={filters.city}
            onChange={e => setFilters({...filters, city: e.target.value})} style={{ padding: "9px 14px", fontSize: 14 }} />
        </div>
        <div className="filter-group">
          <label className="filter-label">Prix max</label>
          <input className="form-input" type="number" placeholder="500 000" value={filters.priceMax}
            onChange={e => setFilters({...filters, priceMax: e.target.value})} style={{ padding: "9px 14px", fontSize: 14 }} />
        </div>
        <div className="filter-group">
          <label className="filter-label">Surface min (m²)</label>
          <input className="form-input" type="number" placeholder="50" value={filters.surfaceMin}
            onChange={e => setFilters({...filters, surfaceMin: e.target.value})} style={{ padding: "9px 14px", fontSize: 14 }} />
        </div>
        <button className="btn btn-secondary btn-sm" style={{ alignSelf: "flex-end" }}
          onClick={() => setFilters({ transaction: "", type: "", city: "", priceMax: "", surfaceMin: "" })}>
          Réinitialiser
        </button>
      </div>

      <p style={{ color: "var(--text-2)", fontSize: 14, marginBottom: 20 }}>
        <strong style={{ color: "var(--text)" }}>{filtered.length} bien{filtered.length !== 1 ? "s" : ""}</strong> trouvé{filtered.length !== 1 ? "s" : ""}
        {user.role === "buyer" && " — triés par compatibilité"}
      </p>

      {filtered.length === 0 ? (
        <div className="empty-state">
          <div style={{ fontSize: 48 }}>🔍</div>
          <h3>Aucun bien trouvé</h3>
          <p>Essayez d'élargir vos critères de recherche</p>
        </div>
      ) : (
        <div className="property-grid">
          {filtered.map(p => (
            <PropertyCard key={p.id} property={p} buyer={user.role === "buyer" ? buyer : null}
              onClick={setSelected} onContact={handleContact} />
          ))}
        </div>
      )}

      {selected && <PropertyModal property={selected} onClose={() => setSelected(null)}
        buyer={user.role === "buyer" ? buyer : null} onContact={handleContact} />}
      {notification && <div className="notification-toast"><Icon.Check />{notification}</div>}
    </div>
  );
}

// ============================================================
// MESSAGES VIEW
// ============================================================
function MessagesView() {
  const CONVERSATIONS = [
    { id: 1, name: "Marie Leclerc", avatar: "ML", property: "Loft Haussmannien", preview: "Bonjour, je suis intéressé par votre bien !", time: "10:32", unread: 2,
      messages: [
        { from: "them", text: "Bonjour ! Vous avez vu mon annonce pour le Loft Haussmannien ?", time: "10:15" },
        { from: "me", text: "Oui, il est magnifique ! Serait-il possible de visiter ce week-end ?", time: "10:28" },
        { from: "them", text: "Bien sûr ! Samedi à 14h vous conviendrait ?", time: "10:30" },
        { from: "them", text: "Je vous envoie l'adresse exacte par message.", time: "10:32" },
      ]
    },
    { id: 2, name: "Thomas Bernard", avatar: "TB", property: "Maison Contemporaine", preview: "Documents envoyés ✓", time: "Hier",
      messages: [
        { from: "me", text: "Bonsoir, votre maison m'intéresse beaucoup.", time: "Hier 18:00" },
        { from: "them", text: "Bonsoir ! Quel aspect vous attire en particulier ?", time: "Hier 18:30" },
        { from: "me", text: "Le jardin et l'architecture. Je peux visiter bientôt ?", time: "Hier 19:00" },
        { from: "them", text: "Documents envoyés ✓", time: "Hier 19:30" },
      ]
    },
    { id: 3, name: "Jean-Marc Faure", avatar: "JF", property: "Appartement Vue Mer", preview: "Merci pour votre intérêt", time: "Lun",
      messages: [
        { from: "them", text: "Votre profil correspond très bien à mon bien !", time: "Lun 11:00" },
        { from: "me", text: "Merci, la vue mer est vraiment un critère important pour nous.", time: "Lun 11:30" },
        { from: "them", text: "Merci pour votre intérêt", time: "Lun 12:00" },
      ]
    },
  ];

  const [active, setActive] = useState(CONVERSATIONS[0]);
  const [msg, setMsg] = useState("");
  const [conversations, setConversations] = useState(CONVERSATIONS);
  const messagesEnd = useRef(null);

  useEffect(() => { messagesEnd.current?.scrollIntoView({ behavior: "smooth" }); }, [active]);

  const sendMessage = () => {
    if (!msg.trim()) return;
    const updated = conversations.map(c => c.id === active.id
      ? { ...c, messages: [...c.messages, { from: "me", text: msg, time: "À l'instant" }], preview: msg }
      : c
    );
    setConversations(updated);
    setActive(updated.find(c => c.id === active.id));
    setMsg("");
  };

  return (
    <div style={{ height: "calc(100vh - 64px)", padding: 28, display: "flex", flexDirection: "column" }}>
      <h2 className="section-title">Messages</h2>
      <div className="chat-layout" style={{ flex: 1 }}>
        <div className="chat-list">
          <div className="chat-list-header">Conversations</div>
          <div className="chat-list-items">
            {conversations.map(c => (
              <div key={c.id} className={`chat-item ${active.id === c.id ? "active" : ""}`} onClick={() => setActive(c)}>
                <div className="chat-avatar">{c.avatar}</div>
                <div className="chat-item-info">
                  <div className="chat-item-name">{c.name}</div>
                  <div className="chat-item-preview">{c.preview}</div>
                  <div style={{ fontSize: 11, color: "var(--text-3)", marginTop: 2 }}>{c.property}</div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4 }}>
                  <div className="chat-item-time">{c.time}</div>
                  {c.unread && <div style={{ background: "var(--primary)", color: "white", fontSize: 10, fontWeight: 700, width: 18, height: 18, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center" }}>{c.unread}</div>}
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="chat-main">
          <div className="chat-header">
            <div className="chat-avatar">{active.avatar}</div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 15 }}>{active.name}</div>
              <div style={{ fontSize: 12, color: "var(--text-2)" }}>📍 {active.property}</div>
            </div>
          </div>
          <div className="chat-messages">
            {active.messages.map((m, i) => (
              <div key={i} className={`message ${m.from === "me" ? "mine" : ""}`}>
                <div className="message-avatar">{m.from === "me" ? "Moi" : active.avatar}</div>
                <div>
                  <div className="message-bubble">{m.text}</div>
                  <span className="message-time">{m.time}</span>
                </div>
              </div>
            ))}
            <div ref={messagesEnd} />
          </div>
          <div className="chat-input">
            <input placeholder="Écrire un message..." value={msg}
              onChange={e => setMsg(e.target.value)}
              onKeyDown={e => e.key === "Enter" && sendMessage()} />
            <button className="btn btn-primary" style={{ width: 42, height: 42, padding: 0, borderRadius: "50%" }} onClick={sendMessage}>
              <Icon.Send />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// PUBLISH PROPERTY VIEW (for sellers)
// ============================================================
function PublishView({ onPublish }) {
  const [form, setForm] = useState({ title: "", type: "appartement", transaction: "vente", price: "", city: "", surface: "", rooms: "", description: "", features: [] });
  const [published, setPublished] = useState(false);
  const featureOptions = ["balcon", "terrasse", "jardin", "parking", "ascenseur", "gardien", "meublé", "cave", "piscine"];

  const toggleFeature = (f) => {
    setForm(prev => ({ ...prev, features: prev.features.includes(f) ? prev.features.filter(x => x !== f) : [...prev.features, f] }));
  };

  if (published) {
    return (
      <div className="content" style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: "60vh" }}>
        <div style={{ fontSize: 72, marginBottom: 20 }}>🎉</div>
        <h2 style={{ fontFamily: "var(--font-display)", fontSize: 28, marginBottom: 12 }}>Bien publié avec succès !</h2>
        <p style={{ color: "var(--text-2)", marginBottom: 28 }}>Votre bien est maintenant visible par les acheteurs potentiels.</p>
        <button className="btn btn-primary" onClick={() => setPublished(false)}><Icon.Plus /> Publier un autre bien</button>
      </div>
    );
  }

  return (
    <div className="content">
      <h2 className="section-title">Publier un bien</h2>
      <div style={{ background: "white", borderRadius: "var(--radius)", border: "1px solid var(--border)", padding: 28, maxWidth: 700 }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, marginBottom: 18 }}>
          <div className="form-group" style={{ gridColumn: "1/-1", marginBottom: 0 }}>
            <label className="form-label">Titre de l'annonce *</label>
            <input className="form-input" placeholder="Ex: Beau T3 lumineux centre-ville" value={form.title} onChange={e => setForm({...form, title: e.target.value})} />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Type de bien</label>
            <select className="form-input form-select" value={form.type} onChange={e => setForm({...form, type: e.target.value})}>
              {["appartement","maison","studio","loft","villa"].map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase()+t.slice(1)}</option>)}
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Transaction</label>
            <select className="form-input form-select" value={form.transaction} onChange={e => setForm({...form, transaction: e.target.value})}>
              <option value="achat">Vente</option>
              <option value="location">Location</option>
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Prix {form.transaction === "location" ? "(€/mois)" : "(€)"} *</label>
            <input className="form-input" type="number" placeholder="350 000" value={form.price} onChange={e => setForm({...form, price: e.target.value})} />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Ville *</label>
            <input className="form-input" placeholder="Paris, Lyon..." value={form.city} onChange={e => setForm({...form, city: e.target.value})} />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Surface (m²) *</label>
            <input className="form-input" type="number" placeholder="75" value={form.surface} onChange={e => setForm({...form, surface: e.target.value})} />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Nombre de pièces</label>
            <input className="form-input" type="number" placeholder="3" value={form.rooms} onChange={e => setForm({...form, rooms: e.target.value})} />
          </div>
          <div className="form-group" style={{ marginBottom: 0, gridColumn: "1/-1" }}>
            <label className="form-label">Description</label>
            <textarea className="form-input" rows={4} placeholder="Décrivez votre bien en détail..." value={form.description}
              onChange={e => setForm({...form, description: e.target.value})} style={{ resize: "vertical" }} />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Équipements</label>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {featureOptions.map(f => (
              <div key={f} onClick={() => toggleFeature(f)}
                style={{ padding: "8px 16px", borderRadius: 20, border: `1.5px solid ${form.features.includes(f) ? "var(--primary)" : "var(--border)"}`,
                  background: form.features.includes(f) ? "var(--primary-light)" : "white", color: form.features.includes(f) ? "var(--primary)" : "var(--text-2)",
                  cursor: "pointer", fontSize: 13, fontWeight: 500, transition: "all 0.2s", display: "flex", alignItems: "center", gap: 6 }}>
                {form.features.includes(f) && <Icon.Check />}{f}
              </div>
            ))}
          </div>
        </div>

        <div style={{ marginTop: 8, padding: 16, background: "var(--primary-light)", borderRadius: "var(--radius-sm)", marginBottom: 20, fontSize: 14, color: "var(--primary)" }}>
          <strong>💡 Conseil imoMatch :</strong> Plus votre annonce est complète, meilleur sera votre taux de matching avec les acheteurs potentiels !
        </div>

        <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
          <button className="btn btn-secondary">Enregistrer en brouillon</button>
          <button className="btn btn-primary" onClick={() => { if (form.title && form.price) { onPublish && onPublish(form); setPublished(true); } }}>
            <Icon.ArrowRight /> Publier l'annonce
          </button>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// MATCHING VIEW (for sellers)
// ============================================================
function MatchingView() {
  const SELLERS_PROPERTY = MOCK_PROPERTIES[0];
  const matchedBuyers = MOCK_BUYERS.map(b => ({ ...b, score: computeMatchScore(b, SELLERS_PROPERTY) })).sort((a, b) => b.score - a.score);

  return (
    <div className="content">
      <h2 className="section-title">Acheteurs compatibles</h2>
      <div style={{ background: "var(--primary-light)", border: "1px solid rgba(232,99,58,0.2)", borderRadius: "var(--radius)", padding: 20, marginBottom: 24, display: "flex", alignItems: "center", gap: 16 }}>
        <div style={{ fontSize: 36 }}>🏠</div>
        <div>
          <div style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 18 }}>{SELLERS_PROPERTY.title}</div>
          <div style={{ color: "var(--text-2)", fontSize: 14 }}>{SELLERS_PROPERTY.city} · {SELLERS_PROPERTY.surface}m² · {SELLERS_PROPERTY.price.toLocaleString()}€</div>
        </div>
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}>
          <ScoreRing score={85} size={52} />
          <span style={{ fontSize: 13, color: "var(--primary)", fontWeight: 600 }}>Score moyen</span>
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {matchedBuyers.map((b, idx) => (
          <div key={b.id} style={{ background: "white", border: "1px solid var(--border)", borderRadius: "var(--radius)", padding: "18px 22px", display: "flex", alignItems: "center", gap: 16, transition: "all 0.2s", cursor: "pointer" }}
            onMouseEnter={e => { e.currentTarget.style.boxShadow = "var(--shadow)"; e.currentTarget.style.borderColor = "transparent"; }}
            onMouseLeave={e => { e.currentTarget.style.boxShadow = ""; e.currentTarget.style.borderColor = "var(--border)"; }}>
            <div style={{ width: 28, height: 28, borderRadius: "50%", background: idx === 0 ? "#FFD700" : idx === 1 ? "#C0C0C0" : "#CD7F32", color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, fontWeight: 800 }}>
              {idx + 1}
            </div>
            <div className="chat-avatar" style={{ width: 50, height: 50 }}>{b.avatar}</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>{b.name}</div>
              <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                <span className="feature-chip">{b.transaction}</span>
                <span className="feature-chip">{b.type}</span>
                <span className="feature-chip">Budget: {b.budget[0].toLocaleString()} – {b.budget[1].toLocaleString()}€</span>
                <span className="feature-chip">{b.surface}m² min · {b.rooms} pièces</span>
              </div>
            </div>
            <div style={{ display: "flex", align: "center", gap: 14 }}>
              <ScoreRing score={b.score} size={52} />
              <button className="btn btn-primary btn-sm"><Icon.Chat /> Contacter</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================
// PROFILE VIEW
// ============================================================
function ProfileView({ user, onLogout }) {
  const [form, setForm] = useState({ transaction: "achat", type: "appartement", city: "Paris", budgetMin: "300000", budgetMax: "600000", surface: "60", rooms: "3", features: [] });
  const featureOpts = ["balcon", "terrasse", "jardin", "parking", "ascenseur", "meublé"];

  return (
    <div className="content">
      <div className="profile-header">
        <div style={{ position: "absolute", right: -60, top: -60, width: 300, height: 300, borderRadius: "50%", background: "rgba(255,255,255,0.04)" }} />
        <div className="profile-avatar-lg">{user.initials}</div>
        <div className="profile-name">{user.name}</div>
        <div className="profile-role">{user.role === "buyer" ? "🔍 Chercheur de bien" : "🏠 Propriétaire vendeur"} · {user.email}</div>
        <div style={{ marginTop: 16, display: "flex", gap: 10 }}>
          <span className="feature-chip" style={{ background: "rgba(255,255,255,0.15)", color: "white" }}>Compte Standard</span>
          <button className="btn btn-sm" style={{ background: "var(--gold)", color: "var(--text)", fontWeight: 700 }}>⭐ Passer Premium</button>
        </div>
      </div>

      {user.role === "buyer" && (
        <div style={{ background: "white", border: "1px solid var(--border)", borderRadius: "var(--radius)", padding: 28 }}>
          <h3 className="section-title">Critères de recherche</h3>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
            {[
              { label: "Transaction", key: "transaction", type: "select", options: [["achat","Achat"],["location","Location"]] },
              { label: "Type de bien", key: "type", type: "select", options: [["appartement","Appartement"],["maison","Maison"],["studio","Studio"]] },
              { label: "Ville souhaitée", key: "city", type: "text", placeholder: "Paris" },
              { label: "Surface min (m²)", key: "surface", type: "number", placeholder: "60" },
              { label: "Budget min (€)", key: "budgetMin", type: "number", placeholder: "300 000" },
              { label: "Budget max (€)", key: "budgetMax", type: "number", placeholder: "600 000" },
              { label: "Nombre de pièces", key: "rooms", type: "number", placeholder: "3" },
            ].map(f => (
              <div key={f.key} className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">{f.label}</label>
                {f.type === "select"
                  ? <select className="form-input form-select" value={form[f.key]} onChange={e => setForm({...form, [f.key]: e.target.value})}>
                      {f.options.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                    </select>
                  : <input className="form-input" type={f.type} placeholder={f.placeholder} value={form[f.key]} onChange={e => setForm({...form, [f.key]: e.target.value})} />
                }
              </div>
            ))}
          </div>

          <div style={{ marginTop: 20 }}>
            <label className="form-label">Équipements souhaités</label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 8 }}>
              {featureOpts.map(f => (
                <div key={f} onClick={() => setForm(prev => ({ ...prev, features: prev.features.includes(f) ? prev.features.filter(x => x !== f) : [...prev.features, f] }))}
                  style={{ padding: "8px 16px", borderRadius: 20, border: `1.5px solid ${form.features.includes(f) ? "var(--primary)" : "var(--border)"}`,
                    background: form.features.includes(f) ? "var(--primary-light)" : "white", color: form.features.includes(f) ? "var(--primary)" : "var(--text-2)",
                    cursor: "pointer", fontSize: 13, fontWeight: 500, transition: "all 0.2s" }}>
                  {f}
                </div>
              ))}
            </div>
          </div>

          <div style={{ marginTop: 24, display: "flex", gap: 10, justifyContent: "flex-end" }}>
            <button className="btn btn-primary"><Icon.Check /> Sauvegarder mes critères</button>
          </div>
        </div>
      )}

      <div style={{ marginTop: 20 }}>
        <button className="btn btn-ghost" style={{ color: "var(--text-2)" }} onClick={onLogout}>
          <Icon.LogOut /> Se déconnecter
        </button>
      </div>
    </div>
  );
}

// ============================================================
// MAIN APP
// ============================================================
export default function App() {
  const [user, setUser] = useState(null);
  const [activeView, setActiveView] = useState("dashboard");
  const [sidebarExpanded, setSidebarExpanded] = useState(false);
  const [properties, setProperties] = useState(MOCK_PROPERTIES);

  const handleLogin = (userData) => setUser(userData);
  const handleLogout = () => { setUser(null); setActiveView("dashboard"); };
  const handlePublish = (form) => {
    const newProp = { ...form, id: Date.now(), price: parseInt(form.price), surface: parseInt(form.surface), rooms: parseInt(form.rooms),
      img: "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=600&q=80",
      owner: { name: user.name, avatar: user.initials, verified: false }, score: 0 };
    setProperties(prev => [newProp, ...prev]);
  };

  if (!user) return <><style>{styles}</style><AuthScreen onLogin={handleLogin} /></>;

  const navItems = user.role === "buyer"
    ? [{ id: "dashboard", icon: <Icon.Home />, label: "Tableau de bord" },
       { id: "search", icon: <Icon.Search />, label: "Rechercher" },
       { id: "messages", icon: <Icon.Chat />, label: "Messages", badge: 2 },
       { id: "profile", icon: <Icon.User />, label: "Mon profil" }]
    : [{ id: "dashboard", icon: <Icon.Home />, label: "Tableau de bord" },
       { id: "publish", icon: <Icon.Plus />, label: "Publier un bien" },
       { id: "matching", icon: <Icon.Search />, label: "Acheteurs matchés" },
       { id: "messages", icon: <Icon.Chat />, label: "Messages", badge: 1 },
       { id: "profile", icon: <Icon.User />, label: "Mon profil" }];

  const titles = { dashboard: "Tableau de bord", search: "Rechercher", messages: "Messages", profile: "Mon profil", publish: "Publier un bien", matching: "Acheteurs matchés" };

  return (
    <>
      <style>{styles}</style>
      <div className="app-layout">
        <aside className={`sidebar ${sidebarExpanded ? "expanded" : ""}`}
          onMouseEnter={() => setSidebarExpanded(true)}
          onMouseLeave={() => setSidebarExpanded(false)}>
          <div className="sidebar-logo" onClick={() => setActiveView("dashboard")}>
            {sidebarExpanded ? <>imo<span>Match</span></> : <>i<span>M</span></>}
          </div>
          {navItems.map(item => (
            <div key={item.id} className={`nav-item ${activeView === item.id ? "active" : ""}`} onClick={() => setActiveView(item.id)}>
              {item.icon}
              {sidebarExpanded && <span>{item.label}</span>}
              {sidebarExpanded && item.badge && <span className="nav-badge">{item.badge}</span>}
              {!sidebarExpanded && item.badge && (
                <div style={{ position: "absolute", top: 8, right: 8, width: 8, height: 8, borderRadius: "50%", background: "var(--primary)", border: "2px solid var(--accent)" }} />
              )}
            </div>
          ))}
          <div className="nav-spacer" />
          <div className="nav-item" onClick={handleLogout} style={{ marginBottom: 8 }}>
            <Icon.LogOut />
            {sidebarExpanded && <span>Déconnexion</span>}
          </div>
        </aside>

        <main className="main">
          <div className="topbar">
            <div className="topbar-title">{titles[activeView]}</div>
            <div className="topbar-actions">
              <div className="icon-btn" onClick={() => setActiveView("messages")}>
                <Icon.Bell />
                <div className="badge">3</div>
              </div>
              <div className="avatar-btn" onClick={() => setActiveView("profile")}>{user.initials}</div>
            </div>
          </div>

          {activeView === "dashboard" && <DashboardView user={user} properties={properties} setActiveView={setActiveView} />}
          {activeView === "search" && <SearchView properties={properties} user={user} />}
          {activeView === "messages" && <MessagesView />}
          {activeView === "profile" && <ProfileView user={user} onLogout={handleLogout} />}
          {activeView === "publish" && <PublishView onPublish={handlePublish} />}
          {activeView === "matching" && <MatchingView />}
        </main>
      </div>
    </>
  );
}
