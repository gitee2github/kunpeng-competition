%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:       hostha
Version:    %{version}
Release:    1%{?dist}
Epoch:      1
Summary:    hostha Service.

License:    ChinaC License
URL:        http://gitlab.chinac.com/Archeros/hsotha
Source:     hostha-%{upstream_version}.tar.gz


BuildArch:      noarch

BuildRequires:  git
BuildRequires:  python-alembic >= 0.8.0
BuildRequires:  python-croniter >= 0.3.4
BuildRequires:  python-devel >= 2.7.5
BuildRequires:  python-eventlet >= 0.17.4
BuildRequires:  python-flask >= 0.10.1
BuildRequires:  python-greenlet >= 0.3.2
BuildRequires:  python-jsonschema >= 2.3.0
BuildRequires:  python-keystoneauth1 >= 2.1.0
BuildRequires:  python-keystonemiddleware >= 4.0.0
BuildRequires:  python-oslo-concurrency >= 3.5.0
BuildRequires:  python-oslo-config >= 2:3.7.0
BuildRequires:  python-oslo-context >= 0.2.0
BuildRequires:  python-oslo-db >= 4.1.0
BuildRequires:  python-oslo-i18n >= 1.5.0
BuildRequires:  python-oslo-log >= 1.8.0
BuildRequires:  python-oslo-messaging >= 4.0.0
BuildRequires:  python-oslo-middleware >= 3.0.0
BuildRequires:  python-oslo-policy >= 0.5.0
BuildRequires:  python-oslo-serialization >= 1.10.0
BuildRequires:  python-oslo-service >= 1.0.0
BuildRequires:  python-oslo-utils >= 3.5.0
BuildRequires:  python-oslo-context >= 0.2.0
BuildRequires:  python-paste-deploy >= 1.5.0
BuildRequires:  python-pbr >= 1.6
BuildRequires:  python-requests >= 2.5.2
BuildRequires:  python-setuptools
BuildRequires:  python-six >= 1.9.0
BuildRequires:  python-sqlalchemy >= 1.0.10
BuildRequires:  python-werkzeug >= 0.9.1
BuildRequires:  pytz
BuildRequires:  python-netifaces >= 0.10.4
BuildRequires:  libvirt-python >= 1.2.17
BuildRequires:  python-tooz >= 1.58.0

Requires:       python-alembic >= 0.8.0
Requires:       python-croniter >= 0.3.4
Requires:       python-eventlet >= 0.17.4
Requires:       python-flask >= 0.10.1
Requires:       python-greenlet >= 0.3.2
Requires:       python-jsonschema >= 2.3.0
Requires:       python-keystoneauth1 >= 2.1.0
Requires:       python-keystonemiddleware >= 4.0.0
Requires:       python-oslo-concurrency >= 3.5.0
Requires:       python-oslo-config >= 2:3.7.0
Requires:       python-oslo-context >= 0.2.0
Requires:       python-oslo-db >= 4.1.0
Requires:       python-oslo-i18n >= 1.5.0
Requires:       python-oslo-log >= 1.8.0
Requires:       python-oslo-messaging >= 4.0.0
Requires:       python-oslo-middleware >= 3.0.0
Requires:       python-oslo-policy >= 0.5.0
Requires:       python-oslo-serialization >= 1.10.0
Requires:       python-oslo-service >= 1.0.0
Requires:       python-oslo-utils >= 3.5.0
Requires:       python-oslo-context >= 0.2.0
Requires:       python-paste-deploy >= 1.5.0
Requires:       python-pbr >= 1.6
Requires:       python-requests >= 2.5.2
Requires:       python-six >= 1.9.0
Requires:       python-sqlalchemy >= 1.0.10
Requires:       python-werkzeug >= 0.9.1
Requires:       pytz
Requires:       python-netifaces >= 0.10.4
Requires:       libvirt-python >= 1.2.17
Requires:       python-tooz >= 1.58.0
Requires:       smartmontools
Requires:       ipmitool

%description
hostha Service.

%prep
%setup -q -n hostha-%{upstream_version}

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

install -d -m 750 %{buildroot}%{_localstatedir}/log/hostha
install -d -m 750 %{buildroot}%{_sysconfdir}/hostha

install -p -D -m 755 package/systemd/hostha-api.service %{buildroot}%{_unitdir}/hostha-api.service

install -p -D -m 755 package/systemd/hostha-hostha.service %{buildroot}%{_unitdir}/hostha-hostha.service
install -p -D -m 640 etc/hostha/hostha.conf  %{buildroot}%{_sysconfdir}/hostha/hostha.conf
install -p -D -m 640 etc/hostha/api-paste.ini  %{buildroot}%{_sysconfdir}/hostha/api-paste.ini
install -p -D -m 640 etc/hostha/policy.json  %{buildroot}%{_sysconfdir}/hostha/policy.json
install -p -D -m 640 etc/logrotate.d/hostha %{buildroot}%{_sysconfdir}/logrotate.d/hostha

%post
%systemd_post hostha-api.service
%systemd_post hostha-hostha.service


%preun
%systemd_preun hostha-api.service
%systemd_preun hostha-hostha.service


%postun
%systemd_postun hostha-api.service
%systemd_postun hostha-hostha.service


%files
%{_bindir}/hostha-api
%{_bindir}/hostha-hostha
%{_bindir}/hostha-db-manage
%dir %{_sysconfdir}/hostha
%config(noreplace) %{_sysconfdir}/hostha/hostha.conf
%config %{_sysconfdir}/hostha/api-paste.ini
%config(noreplace) %{_sysconfdir}/hostha/policy.json
%config(noreplace) %{_sysconfdir}/logrotate.d/hostha
%{_unitdir}/hostha-api.service
%{_unitdir}/hostha-hostha.service

%dir %attr(0750, root, root) %{_localstatedir}/log/hostha
%{python2_sitelib}/hostha
%{python2_sitelib}/hostha-*.egg-info
