Name:       {NAME}
Version:    {VERSION}
Release:    1%{?dist}
Summary:    {SYNOPSIS}
License:    Commercial
URL:        https://heisenware.com
Group:      Networking
Requires:   logrotate, systemd
Packager:   Burkhard Heisen <burkhard.heisenware@heisenware.com>

%define _rpmdir {OUTPUT_DIR}
%define _logdir /var/log/heisenware
%define _unitdir /usr/lib/systemd/system

%description
{SYNOPSIS}
{DESCRIPTION}

%prep
# binary package, no sources

%build
# binary package, nothing to build

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}/etc/logrotate.d
mkdir -p %{buildroot}%{_logdir}

install -m 0755 {HEISENWARE_AGENT_BINARY} %{buildroot}%{_bindir}/{HEISENWARE_AGENT_BINARY}
install -m 0644 {NAME}.service %{buildroot}%{_unitdir}/{NAME}.service
install -m 0644 {NAME} %{buildroot}/etc/logrotate.d/{NAME}

%pre
systemctl is-active {NAME}.service > /dev/null 2>&1 && systemctl stop {NAME}.service || :   

%post
systemctl enable --now {NAME}.service >/dev/null 2>&1 || :

%preun
systemctl stop {NAME}.service || :

%postun
systemctl daemon-reload

%files
%{_bindir}/{HEISENWARE_AGENT_BINARY}
%{_unitdir}/{NAME}.service
%config(noreplace) /etc/logrotate.d/{NAME}
%dir %attr(0755, root, root) %{_logdir}
%license LICENSE

%changelog
* {DATE} - {VERSION}-1
- Generated the package