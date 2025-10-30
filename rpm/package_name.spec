Name:       {NAME}
Version:    {VERSION}
Release:    1%{?dist}
Summary:    {SYNOPSIS}
License:    commercial
URL:        https://heisenware.com
BuildArch:  {ARCH}
Requires:   logrotate, systemd

%define _rpmdir {OUTPUT_DIR}
%define _logdir /var/log/heisenware
%define _unitdir /usr/lib/systemd/system

%description
{SYNOPSIS} {DESCRIPTION}

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
install -m 0644 {NAME}.conf %{buildroot}/etc/logrotate.d/{NAME}.conf

%pre
if [ systemctl is-enabled {NAME}.service && 
     systemctl is-active --quiet {NAME}.service ]; 
then
    systemctl stop {NAME}.service
fi

%post
if [ ! $(systemctl is-enabled {NAME}.service) ]; 
then
    systemctl enable {NAME}.service
    systemctl start {NAME}.service
fi

%preun
if [ systemctl is-enabled {NAME}.service && 
     systemctl is-active --quiet {NAME}.service ]; 
then
    systemctl stop {NAME}.service
fi

%postun
systemctl daemon-reload

%files
%{_bindir}/{HEISENWARE_AGENT_BINARY}
%{_unitdir}/{NAME}.service
/etc/logrotate.d/{NAME}.conf
%dir %attr(644, root, root) %{_logdir}
%license LICENSE

%changelog
# no changes to log