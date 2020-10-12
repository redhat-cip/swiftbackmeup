%if 0%{?rhel} && 0%{?rhel} < 8
%global with_python2 1
%else
%global with_python3 1
%endif
%global srcname swiftbackmeup

Name:           %{srcname}
Version:        0.0.5
Release:        VERS%{?dist}

Summary:        Swift Backmeup
License:        ASL 2.0
URL:            https://pypi.io/pypi/%{srcname}
Source0:        https://pypi.io/packages/source/s/%{srcname}/%{srcname}-%{version}.tar.gz

BuildArch:      noarch

%if 0%{?with_python2}
BuildRequires:  python2-devel
BuildRequires:  python2-setuptools
Requires:       python-prettytable
Requires:       PyYAML
Requires:       python2-keystoneclient
Requires:       python2-swiftclient
%else
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
Requires:       python3-prettytable
Requires:       python3-pyyaml
Requires:       python3-keystoneclient
Requires:       python3-swiftclient
%endif

%description
Tools to backup artifats into a Swift Object store


%prep
%autosetup -n %{srcname}-%{version}


%build
%if 0%{?with_python2}
%py2_build
%else
%py3_build
%endif


%install
%if 0%{?with_python2}
%py2_install
%else
%py3_install
%endif


%files
%doc README.md
%if 0%{?with_python2}
%{python2_sitelib}/%{srcname}
%{python2_sitelib}/*.egg-info
%else
%{python3_sitelib}/%{srcname}
%{python3_sitelib}/*.egg-info
%endif
%{_bindir}/%{srcname}
