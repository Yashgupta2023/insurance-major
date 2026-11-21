import { useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import { BarChart3, Bell, ChevronDown, ClipboardCheck, LayoutDashboard, Moon, ShieldAlert, Sun, WalletCards, FileText, Users, Building2, LogOut, Search, Plus } from 'lucide-react'
import { BrowserRouter, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { api } from './services/api'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import './App.css'

const demoClaims=[
	{ id: 'CLM-1024', customer: 'Aarav Sharma', type: 'Motor Accident', amount: '₹1,20,000', date: '21 Oct 2026', risk: 82, category: 'HIGH', status: 'SUBMITTED' },
	{ id: 'CLM-1025', customer: 'Meera Kapoor', type: 'Health', amount: '₹28,000', date: '20 Oct 2026', risk: 18, category: 'LOW', status: 'APPROVED' },
	{ id: 'CLM-1026', customer: 'Rohan Mehta', type: 'Motor Repair', amount: '₹85,000', date: '18 Oct 2026', risk: 48, category: 'MEDIUM', status: 'INVESTIGATION' }
]

function Login() {
	const nav = useNavigate();
	const [email, setEmail] = useState('investigator@demo.com');
	const [password, setPassword] = useState('Demo@123');
	const [error, setError] = useState('');
	async function submit(e: FormEvent) {
		e.preventDefault();
		setError('');
		try {
			const { data } = await api.post('/auth/login', { email, password });
			localStorage.setItem('token', data.access_token);
			localStorage.setItem('user', JSON.stringify(data.user));
			nav(data.user.role === 'Customer' ? '/customer' : data.user.role === 'Admin' ? '/admin' : '/investigator')
		} catch {
			setError('Unable to sign in. Ensure the backend is running and PostgreSQL is configured.')
		}
	}
	return <div className="login-page">
		<div className="login-brand">
			<div className="brand-mark"><ShieldAlert /></div>
			<h1>ClaimIQ</h1>
			<p>Insurance intelligence platform</p>
		</div>
		<form className="login-card" onSubmit={submit}>
			<span className="eyebrow">SECURE ACCESS</span>
			<h2>Welcome back</h2>
			<p>Sign in to continue to ClaimIQ</p>
			<label>Email address<input value={email} onChange={e => setEmail(e.target.value)} type="email" /></label>
			<label>Password<input value={password} onChange={e => setPassword(e.target.value)} type="password" /></label>
			{error && <div className="error">{error}</div>}
			<button className="primary-btn">Sign in</button>
			<div className="demo-box">
				<b>Demo accounts</b>
				<div>Customer · customer@demo.com</div>
				<div>Investigator · investigator@demo.com</div>
				<div>Admin · admin@demo.com</div>
				<div>Password for all: <b>Demo@123</b></div>
			</div>
		</form>
	</div>
}

function Shell({ children }: { children: ReactNode }) {
	const [dark, setDark] = useState(false);
	const [open, setOpen] = useState(true);
	const user = JSON.parse(localStorage.getItem('user') || '{"name":"Demo User","role":"Investigator","email":"investigator@demo.com"}');
	const nav = useNavigate();
	const role = user.role;

	const links = role === 'Customer' ? [['Overview', LayoutDashboard, '/customer'], ['My claims', FileText, '/customer'], ['Policies', WalletCards, '/customer']] :
		role === 'Admin' ? [['Overview', LayoutDashboard, '/admin'], ['Users', Users, '/admin'], ['Policies', WalletCards, '/admin'], ['Providers', Building2, '/admin'], ['Analytics', BarChart3, '/admin']] :
			[['Overview', LayoutDashboard, '/investigator'], ['Investigations', ClipboardCheck, '/investigator'], ['High-risk claims', ShieldAlert, '/investigator'], ['Analytics', BarChart3, '/investigator']]

	function logout() { localStorage.clear(); nav('/login') }
	return <div className={dark ? 'app dark' : 'app'}>
		<aside className={open ? 'sidebar' : 'sidebar collapsed'}>
			<div className="side-brand">
				<div className="brand-mark"><ShieldAlert /></div>
				{open && <strong>ClaimIQ</strong>}
			</div>
			<nav>
				{links.map(([name, Icon, path]: any) => <button key={name} onClick={() => nav(path)}><Icon /><span>{name}</span></button>)}
			</nav>
			<button className="collapse" onClick={() => setOpen(!open)}>«</button>
		</aside>
		<div className="main">
			<header>
				<div className="search">
					<Search />
					<input placeholder="Search claims, customers, policy numbers..." />
				</div>
				<div className="header-actions">
					<button onClick={() => setDark(!dark)}>{dark ? <Sun /> : <Moon />}</button>
					<button className="notification"><Bell /><i /></button>
					<div className="avatar">{user.name?.[0] || 'U'}</div>
					<div className="profile">
						<b>{user.name}</b>
						<small>{role}</small>
					</div>
					<ChevronDown />
					<button className="logout" title="Logout" onClick={logout}><LogOut /></button>
				</div>
			</header>
			<main>{children}</main>
		</div>
	</div>
}

function Stat({ label, value, color, icon: Icon }: { label: string, value: string | number, color: string, icon: any }) {
	return <div className="stat">
		<div style={{ background: color }}><Icon /></div>
		<div>
			<small>{label}</small>
			<strong>{value}</strong>
		</div>
	</div>
}
function ClaimsTable() {
	return <div className="card table-card">
		<div className="card-head">
			<div>
				<h3>Recent claims</h3>
				<p>Prioritized by fraud risk and submission date</p>
			</div>
			<button className="outline-btn"><Search /> Filter</button>
		</div>
		<div className="table-wrap">
			<table>
				<thead>
					<tr>
						<th>Claim ID</th>
						<th>Customer</th>
						<th>Category</th>
						<th>Amount</th>
						<th>Submitted</th>
						<th>Risk score</th>
						<th>Status</th>
					</tr>
				</thead>
				<tbody>
					{demoClaims.map(c =>
						<tr key={c.id}>
							<td><b>{c.id}</b></td>
							<td>{c.customer}</td>
							<td>{c.type}</td>
							<td>{c.amount}</td>
							<td>{c.date}</td>
							<td><span className={`risk ${c.category.toLowerCase()}`}>{c.risk} · {c.category}</span></td>
							<td><span className="status">{c.status}</span></td>
						</tr>
					)}
				</tbody>
			</table>
		</div>
	</div>
}

function Investigator() {
	const data = [
		{ name: 'May', value: 38 },
		{ name: 'Jun', value: 48 },
		{ name: 'Jul', value: 43 },
		{ name: 'Aug', value: 68 },
		{ name: 'Sep', value: 57 },
		{ name: 'Oct', value: 76 }
	];
	return <Shell>
		<div className="page-title">
			<div>
				<span className="eyebrow">INVESTIGATION CENTER</span>
				<h1>Claim overview</h1>
			</div>
			<button className="primary-btn"><ClipboardCheck /> Review queue</button>
		</div>
		<div className="stats">
			<Stat label="Total claims" value="128" color="#2563eb" icon={FileText} />
			<Stat label="Pending reviews" value="24" color="#f59e0b" icon={ClipboardCheck} />
			<Stat label="High-risk claims" value="9" color="#ef4444" icon={ShieldAlert} />
			<Stat label="Approved" value="67" color="#10b981" icon={ClipboardCheck} />
		</div>
		<div className="grid-2">
			<ClaimsTable />
			<div className="card chart-card">
				<div className="card-head">
					<div>
						<h3>Claims trend</h3>
						<p>Monthly claim volume</p>
					</div>
				</div>
				<ResponsiveContainer width="100%" height={270}>
					<AreaChart data={data}>
						<defs>
							<linearGradient id="blue" x1="0" y1="0" x2="0" y2="1">
								<stop offset="5%" stopColor="#2563eb" stopOpacity={.25} />
								<stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
							</linearGradient>
						</defs>
						<CartesianGrid strokeDasharray="3 3" vertical={false} />
						<XAxis dataKey="name" />
						<YAxis />
						<Tooltip />
						<Area type="monotone" dataKey="value" stroke="#2563eb" fill="url(#blue)" strokeWidth={3} />
					</AreaChart>
				</ResponsiveContainer>
			</div>
		</div>
	</Shell>
}

function Customer() {
	return <Shell>
		<div className="page-title">
			<div>
				<span className="eyebrow">CUSTOMER PORTAL</span>
				<h1>Welcome back</h1>
			</div>
			<button className="primary-btn"><Plus /> Submit new claim</button>
		</div>
		<div className="stats">
			<Stat label="Total claims" value="6" color="#2563eb" icon={FileText} />
			<Stat label="Under review" value="2" color="#f59e0b" icon={ClipboardCheck} />
			<Stat label="Approved" value="3" color="#10b981" icon={ClipboardCheck} />
			<Stat label="Rejected" value="1" color="#ef4444" icon={ShieldAlert} />
		</div>
		<div className="grid-2">
			<ClaimsTable />
			<div className="card policy-card">
				<span className="eyebrow">ACTIVE POLICY</span>
				<h3>POL-1001</h3>
				<p>Health & Motor</p>
				<div className="coverage">
					<span>Coverage limit</span>
					<strong>₹5,00,000</strong>
				</div>
				<div className="coverage">
					<span>Validity</span>
					<strong>31 Dec 2027</strong>
				</div>
				<button className="outline-btn">View policy</button>
			</div>
		</div>
	</Shell>
}

function Admin() {
	return <Shell>
		<div className="page-title">
			<div>
				<span className="eyebrow">SYSTEM ADMINISTRATION</span>
				<h1>Administration</h1>
			</div>
		</div>
		<div className="stats">
			<Stat label="Total users" value="19" color="#2563eb" icon={Users} />
			<Stat label="Active policies" value="10" color="#10b981" icon={WalletCards} />
			<Stat label="Providers" value="10" color="#8b5cf6" icon={Building2} />
			<Stat label="Fraud alerts" value="9" color="#ef4444" icon={ShieldAlert} />
		</div>
		<ClaimsTable />
	</Shell>
}

function Protected({ role, children }: { role: string, children: React.ReactNode }) {
	const user = localStorage.getItem('user');
	if (!user) return <Navigate to="/login" />;
	const parsed = JSON.parse(user);
	return parsed.role === role ? children : <Navigate to={parsed.role === 'Customer' ? '/customer' : parsed.role === 'Admin' ? '/admin' : '/investigator'} />
}
export default function App() {
	return <BrowserRouter>
		<Routes>
			<Route path="/login" element={<Login />} />
			<Route path="/investigator" element={<Protected role="Investigator"><Investigator /></Protected>} />
			<Route path="/customer" element={<Protected role="Customer"><Customer /></Protected>} />
			<Route path="/admin" element={<Protected role="Admin"><Admin /></Protected>} />
			<Route path="*" element={<Navigate to="/login" />} />
		</Routes>
	</BrowserRouter>
}
