import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button, Input } from '../components/ui';
import './Auth.css';

const INITIAL_SIGNUP_FORM = {
  email: '',
  full_name: '',
  organization_name: '',
  password: '',
  role: 'member',
};

export default function SignupPage() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [signupForm, setSignupForm] = useState(INITIAL_SIGNUP_FORM);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const updateSignupField = (field) => (event) => {
    setSignupForm(current => ({ ...current, [field]: event.target.value }));
  const [form, setForm] = useState(INITIAL_SIGNUP_FORM);
  const [form, setForm] = useState({ email: '', full_name: '', organization_name: '', password: '', role: 'member' });


  

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (k) => (e) => {
    const value = e.target.value;
    setForm((f) => {
      if (k !== 'email') return { ...f, [k]: value };
      const orgGuess = value.includes('@') ? value.split('@')[1].split('.')[0] : '';
      return { ...f, email: value, organization_name: orgGuess };
    });

  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const me = await signup(signupForm);
      navigate(me?.role === 'admin' ? '/manager-dashboard' : '/member-dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-bg">
        <div className="auth-grid" />
      </div>
      <div className="auth-card animate-fade">
        <div className="auth-brand">
          <div className="auth-mark">T</div>
          <span>TaskFlow</span>
        </div>
        <div className="auth-heading">
          <h1>Create account</h1>
          <p>Start managing your team's work</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <Input
            id="full_name" label="Full name"
            value={signupForm.full_name} onChange={updateSignupField('full_name')}
            placeholder="Jane Smith" required
          />
          <Input
            id="organization_name" label="Organization name"

            value={signupForm.organization_name} onChange={updateSignupField('organization_name')}

            value={form.organization_name} onChange={set('organization_name')}

            placeholder="Acme Corp" required
          />
          <Input
            id="email" label="Email" type="email"
            value={signupForm.email} onChange={updateSignupField('email')}
            placeholder="you@company.com" required
          />
          <Input
            id="organization_name" label="Organization"
            value={form.organization_name} onChange={set('organization_name')}

            placeholder="Auto from email domain" required


            placeholder="Auto from email domain" required

            placeholder="Acme Inc" required


          />
          <Input
            id="password" label="Password" type="password"
            value={signupForm.password} onChange={updateSignupField('password')}
            placeholder="Min 8 chars, include number + capital"
            required
          />
          <div className="input-wrap">
            <label htmlFor="role" className="input-label">Account type</label>

            <select id="role" className="input" value={signupForm.role} onChange={updateSignupField('role')}>

            <select id="role" className="input" value={form.role} onChange={set('role')}>

              <option value="admin">Admin</option>
              <option value="member">Member</option>
            </select>
          </div>
          {error && <div className="auth-error">{error}</div>}
          <Button type="submit" loading={loading} size="lg" style={{ width: '100%', justifyContent: 'center' }}>
            Create account
          </Button>
        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  );
}
