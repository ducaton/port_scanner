Name:           duc_port_scanner
Version:        1.0
Release:        1%{?dist}
Summary:        Server to scan ports of given IP

License:        GPLv3
URL:            https://github.com/ducaton/port_scanner
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python3
Requires:       python3
Requires:       python3-aiohttp

%global debug_package %{nil}

%description
Server to scan ports of given IP

%prep
%autosetup


%build

%install
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/usr/lib/%{name}

cat > %{buildroot}/%{_bindir}/%{name} <<-EOF
#!/bin/bash
/usr/bin/python3 /usr/lib/%{name}/%{name}.py
EOF

chmod 0755 %{buildroot}/%{_bindir}/%{name}

install -Dpm 644 %{name}.py %{buildroot}/usr/lib/%{name}/%{name}.py
install -Dpm 644 %{name}.service %{buildroot}%{_unitdir}/%{name}.service


%files
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
/usr/lib/%{name}/%{name}.py
/usr/lib/%{name}



%changelog
* Mon Jun 20 16:44:35 +05 2022 ducaton <102594550+ducaton@users.noreply.github.com>
- 
