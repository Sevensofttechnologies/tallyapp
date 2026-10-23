let currentCompanyId = null;

function formatApiError(error) {
  if (!error) return 'Unknown error';
  if (typeof error === 'string') return error;

  const backendError = error.error;
  if (backendError) {
    const details = backendError.details;
    if (details && details.errors) {
      try {
        return JSON.stringify(details.errors);
      } catch (e) {
        return String(backendError.message || 'Request failed');
      }
    }
    return String(backendError.message || 'Request failed');
  }

  if (error.detail) {
    try {
      return typeof error.detail === 'string' ? error.detail : JSON.stringify(error.detail);
    } catch (e) {
      return String(error.detail);
    }
  }

  return error.message || 'Request failed';
}

async function loadEmailSettings() {
  const company = Auth.getActiveCompany();
  if (!company) {
    Toast.warning('Please select a company first');
    window.location.href = 'dashboard.html?selectCompany=true';
    return;
  }
  currentCompanyId = company.id;

  try {
    const res = await API.adminEmailSettings.get(currentCompanyId);
    const data = res && typeof res === 'object' && 'data' in res ? res.data : res;

    document.getElementById('smtp_host').value = data.smtp_host || '';
    document.getElementById('smtp_port').value = data.smtp_port || 587;
    document.getElementById('smtp_user').value = data.smtp_user || '';

    document.getElementById('from_email').value = data.from_email || '';
    document.getElementById('from_name').value = data.from_name || '';
    document.getElementById('reply_to').value = data.reply_to || '';

    document.getElementById('use_tls').value = (data.use_tls ? 'true' : 'false');
    document.getElementById('use_ssl').value = (data.use_ssl ? 'true' : 'false');

    document.getElementById('password_state').textContent = data.has_password
      ? 'Password is set (stored encrypted). Leave password blank to keep it unchanged.'
      : 'Password is not set. Please enter SMTP app password and save.';

  } catch (error) {
    Toast.error(formatApiError(error) || 'Failed to load email settings');
  }
}

window.saveEmailSettings = async function () {
  if (!Auth.hasRole('admin')) {
    Toast.error('Admin access required');
    return;
  }

  if (!currentCompanyId) {
    const company = Auth.getActiveCompany();
    currentCompanyId = company?.id;
  }

  const companyIdInt = parseInt(String(currentCompanyId || ''), 10);
  if (!companyIdInt) {
    Toast.error('Please select a company first');
    return;
  }

  const payload = {
    company_id: companyIdInt,
    smtp_host: document.getElementById('smtp_host').value,
    smtp_port: parseInt(document.getElementById('smtp_port').value || '587', 10),
    smtp_user: document.getElementById('smtp_user').value || null,
    smtp_password: document.getElementById('smtp_password').value || null,
    use_tls: document.getElementById('use_tls').value === 'true',
    use_ssl: document.getElementById('use_ssl').value === 'true',
    from_email: document.getElementById('from_email').value,
    from_name: document.getElementById('from_name').value || null,
    reply_to: document.getElementById('reply_to').value || null,
  };

  try {
    const res = await API.adminEmailSettings.save(payload);
    if (res && typeof res === 'object' && res.success === false) {
      throw res;
    }
    document.getElementById('smtp_password').value = '';
    Toast.success('Email settings saved');
    await loadEmailSettings();
  } catch (error) {
    Toast.error(formatApiError(error) || 'Failed to save email settings');
  }
};

window.sendTestEmail = async function () {
  if (!Auth.hasRole('admin')) {
    Toast.error('Admin access required');
    return;
  }

  if (!currentCompanyId) {
    const company = Auth.getActiveCompany();
    currentCompanyId = company?.id;
  }

  const companyIdInt = parseInt(String(currentCompanyId || ''), 10);
  if (!companyIdInt) {
    Toast.error('Please select a company first');
    return;
  }

  const to = document.getElementById('test_to').value;
  if (!to) {
    Toast.error('Test recipient email is required');
    return;
  }

  try {
    const res = await API.adminEmailSettings.test({
      company_id: companyIdInt,
      to_email: to,
      subject: 'TallyBridge SMTP Test',
      body: 'This is a test email from TallyBridge.'
    });
    if (res && typeof res === 'object' && res.success === false) {
      throw res;
    }
    Toast.success('Test email sent');
  } catch (error) {
    Toast.error(formatApiError(error) || 'Test email failed');
  }
};

document.addEventListener('DOMContentLoaded', () => {
  if (!Auth.isAuthenticated()) {
    window.location.href = 'login.html';
    return;
  }

  const user = Auth.getUser();
  if (user) {
    const nameEl = document.getElementById('user-name');
    const roleEl = document.getElementById('user-role-display');
    const initialsEl = document.getElementById('user-initials');
    if (nameEl) nameEl.textContent = `${user.first_name} ${user.last_name}`;
    if (roleEl) roleEl.textContent = Utils.capitalize(user.role);
    if (initialsEl) initialsEl.textContent = Utils.getInitials(`${user.first_name} ${user.last_name}`);
  }

  if (!Auth.hasRole('admin')) {
    Toast.error('Admin access required');
    window.location.href = 'dashboard.html';
    return;
  }

  loadEmailSettings();
});
