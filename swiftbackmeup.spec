%global srcname swiftbackmeup

Name:           %{srcname}
Version:        0.0.5
Release:        VERS%{?dist}

Summary:        Swift Backmeup
License:        ASL 2.0
URL:            https://pypi.io/pypi/%{srcname}
Source0:        https://pypi.io/packages/source/s/%{srcname}/%{srcname}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python2-setuptools

Requires:       python-prettytable
Requires:       PyYAML
Requires:       python2-keystoneclient
Requires:       python2-swiftclient

%description
Tools to backup artifats into a Swift Object store


%prep
%autosetup -n %{srcname}-%{version}


%build
%py2_build


%install
%py2_install


%files
%doc README.md
%{python2_sitelib}/%{srcname}
%{python2_sitelib}/*.egg-info
%{_bindir}/%{srcname}
