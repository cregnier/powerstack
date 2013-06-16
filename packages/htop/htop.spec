Name:		htop
Version:	1.0.2
Release:	1
Summary:	Interactive process viewer for Linux

Group:		Applications/System
License:	GPLv2
URL:		http://htop.sourceforge.net
Source0:	http://download.sourceforge.net/htop/%{name}-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:	ncurses-devel
Requires:	ncurses

%description
htop is an interactive process viewer for Linux, that aims to be a
better "top".


%prep
%setup -q


%build
# FIXME: ioprio_set() system call is available since kernel >= 2.6.13, disable "--enable-taskstats" feature on CentOS-4
%configure --enable-openvz \
	--enable-vserver \
	--enable-cgroup \
%if 0%{?rhel} >= 5
	--enable-taskstats \
%endif
	--enable-unicode \
	--enable-native-affinity
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

# Remove htop desktop related stuff, PowerStack is focused on server environment
rm %{buildroot}/usr/share/applications/htop.desktop %{buildroot}/usr/share/pixmaps/htop.png


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING ChangeLog README
%{_bindir}/htop
%{_mandir}/man1/htop.1*


%changelog
* Thu Jun 13 2013 Santi Saez <santi@woop.es> - 1.0.2-1
- htop 1.0.2 packaged from scratch
