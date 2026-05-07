import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button, Input } from '../components/ui';
import './Auth.css';

const INITIAL_SIGNUP_FORM = {
  full_name: '',
  organization_name: '',
  email: '',
  password: '',
  role: 'member',
};

function organizationFromEmail(email) {
  const domain = email.includes('@') ? email.split('@')[1] : '';
  const organization = domain ? domain.split('.')[0] : '';
  return organization ? organization.charAt(0).toUpperCase() + organization.slice(1) : '';
}

export default function SignupPage() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [accountForm, setAccountForm] = useState(INITIAL_SIGNUP_FORM);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const updateField = (field) => (event) => {
    const value = event.target.value;

    setAccountForm(current => {
      if (field !== 'email') {
        return { ...current, [field]: value };
      }

      const guessedOrganization = organizationFromEmail(value);
      const previousGuessedOrganization = organizationFromEmail(current.email);
      const shouldAutoFillOrganization =
        !current.organization_name || current.organization_name === previousGuessedOrganization;

      return {
        ...current,
        email: value,
        organization_name: shouldAutoFillOrganization
          ? guessedOrganization
          : current.organization_name,
      };
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      const me = await signup(accountForm);
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
            id="full_name"
            label="Full name"
            value={accountForm.full_name}
            onChange={updateField('full_name')}
            placeholder="Jane Smith"
            required
          />
          <Input
            id="email"
            label="Email"
            type="email"
            value={accountForm.email}
            onChange={updateField('email')}
            placeholder="you@company.com"
            required
          />
          <Input
            id="organization_name"
            label="Organization name"
            value={accountForm.organization_name}
            onChange={updateField('organization_name')}
            placeholder="Acme Corp"
            required
          />
          <Input
            id="password"
            label="Password"
            type="password"
            value={accountForm.password}
            onChange={updateField('password')}
            placeholder="Min 8 chars, include number + capital"
            required
          />
          <div className="input-wrap">
            <label htmlFor="role" className="input-label">Account type</label>
            <select
              id="role"
              className="input"
              value={accountForm.role}
              onChange={updateField('role')}
            >
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
