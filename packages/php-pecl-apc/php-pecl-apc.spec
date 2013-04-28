%{!?__pecl: %{expand: %%global __pecl %{_bindir}/pecl}}
%define php_extdir %(php-config --extension-dir 2>/dev/null || echo %{_libdir}/php4)
%global php_zendabiver %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP Extension => //p') | tail -1)
%global php_version %((echo 0; php-config --version 2>/dev/null) | tail -1)
%define pecl_name APC

# svn checkout -r %{svn_revision} https://svn.php.net/repository/pecl/apc/trunk apc-svn-%{svn_revision}
# tar czfv apc-svn-%{svn_revision}.tgz apc-svn-%{svn_revision}
#%global svn_revision	324546

Summary:       APC caches and optimizes PHP intermediate code
Name:          php-pecl-apc
Version:       3.1.13
Release:       1
License:       PHP
Group:         Development/Languages
URL:           http://pecl.php.net/package/APC
#Source:       APC-%{version}-%{svn_revision}.tgz
Source:        http://pecl.php.net/get/APC-%{version}.tgz
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root
Conflicts:     php-mmcache, php-eaccelerator
BuildRequires: php-devel >= 5.1.0, httpd-devel, php-pear, pcre-devel

Requires(post): %{__pecl}
Requires(postun): %{__pecl}

%if %{?php_zend_api}0
# Require clean ABI/API versions if available (Fedora)
Requires:      php(zend-abi) = %{php_zend_api}
Requires:      php(api) = %{php_core_api}
%else
%if "%{rhel}" == "5"
# RHEL5 where we have php-common providing the Zend ABI the "old way"
Requires:      php-zend-abi = %{php_zendabiver}
%else
# RHEL4 where we have no php-common and nothing providing the Zend ABI...
Requires:      php = %{php_version}
%endif
%endif
Provides:      php-pecl(%{pecl_name}) = %{version}

# Use APC default configuration file provided by PowerStack
Source1:	apc.ini


%description
APC is a free, open, and robust framework for caching and optimizing PHP
intermediate code.


%package devel
Summary:       APC development files
Group:         Development/Libraries
Requires:      php-pecl-apc = %{version}-%{release}
Requires:      php-devel

%description devel
Files needed to compile programs using APC serializer


%prep
%setup -q -c


%build

# APC svn checkout?
%if 0%{?svn_revision:0}
mv apc-svn-%{svn_revision}/package.xml .
mv apc-svn-%{svn_revision} APC-%{version}
%endif

cd APC-%{version}
%{_bindir}/phpize

# When APC is compiled with mmap support (Memory Mapping), it will use only one
# memory segment, unlike when APC is built with SHM (SysV Shared Memory)
# support that uses multiple memory segments. MMAP does not have a maximum
# limit like SHM does in /proc/sys/kernel/shmmax. In general MMAP support is
# recommeded because it will reclaim the memory faster when the webserver is
# restarted and all in all reduces memory allocation impact at startup.
%configure --enable-apc-mmap --with-php-config=%{_bindir}/php-config

%{__make} %{?_smp_mflags}


%install
pushd APC-%{version}
%{__rm} -rf %{buildroot}
%{__make} install INSTALL_ROOT=%{buildroot}

# Fix the charset of NOTICE
iconv -f iso-8859-1 -t utf8 NOTICE > NOTICE.utf8
mv NOTICE.utf8 NOTICE

popd
# Install package XML file + apc.ini
%{__mkdir_p} %{buildroot}%{pecl_xmldir}
%{__install} -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml
%{__mkdir_p} %{buildroot}%{_sysconfdir}/php.d
%{__install} -m 644 %{SOURCE1} %{buildroot}/etc/php.d/apc.ini


%check
cd %{pecl_name}-%{version}
TEST_PHP_EXECUTABLE=$(which php) php run-tests.php \
    -n -q -d extension_dir=modules \
    -d extension=apc.so \
|| true # 1 test fails http://pecl.php.net/bugs/bug.php?id=16793


%if 0%{?pecl_install:1}
%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null 2>&1 || :
%endif


%if 0%{?pecl_uninstall:1}
%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null 2>&1 || :
fi
%endif


%clean
%{__rm} -rf %{buildroot}


%files
%defattr(-, root, root, 0755)
%doc APC-%{version}/TECHNOTES.txt APC-%{version}/CHANGELOG APC-%{version}/LICENSE
%doc APC-%{version}/NOTICE        APC-%{version}/TODO      APC-%{version}/apc.php
%doc APC-%{version}/INSTALL
%config(noreplace) %{_sysconfdir}/php.d/apc.ini
%{php_extdir}/apc.so
%{pecl_xmldir}/%{name}.xml


%files devel
%{_includedir}/php/ext/apc


%changelog
* Thu Apr 25 2013 Santi Saez <santi@woop.es> - 3.1.13-1
- Upgrade to APC 3.1.3 (http://kcy.me/jid1)

* Mon Mar 26 2012 Santi Saez <santi@woop.es> - 3.1.9-3
- APC v3.1.9 is not compatible with PHP 5.4, pull changes from SVN revision 324546

* Sat Mar 10 2012 Santi Saez <santi@woop.es> - 3.1.9-2
- PHP 5.4.x ABI support mass rebuild

* Tue Jul 12 2011 Santi Saez <santi@woop.es> - 3.1.9-1
- Updated to APC 3.1.9 + added -devel package for APC serializer

* Sat Apr 10 2010 Joe Orton <jorton@redhat.com> - 3.1.3p1-1.2.1
- hide scriptlet errors (#579036)

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 3.1.3p1-1.1
- Rebuilt for RHEL 6

* Fri Aug 14 2009 Remi Collet <Fedora@FamilleCollet.com> - 3.1.3p1-1
- update to 3.1.3 patch1 (beta, for PHP 5.3 support)
- add test suite (disabled for http://pecl.php.net/bugs/bug.php?id=16793)
- add use_request_time, lazy_classes, lazy_functions options (apc.ini)

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun Jul 12 2009 Remi Collet <Fedora@FamilleCollet.com> - 3.1.2-1
- update to 3.1.2 (beta) - PHP 5.3 support
- use setup -q -c

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.19-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jun 25 2008 Tim Jackson <rpm@timj.co.uk> - 3.0.19-1
- Update to 3.0.19
- Fix PHP Zend API/ABI dependencies to work on EL-4/5
- Fix "License" tag
- Fix encoding of "NOTICE" file
- Add registration via PECL

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 3.0.14-3
- Autorebuild for GCC 4.3

* Tue Aug 28 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 3.0.14-2
- Rebuild for selinux ppc32 issue.

* Thu Jun 28 2007 Chris Chabot <chabotc@xs4all.nl> - 3.0.14-1
- Updated to 3.0.14
- Included new php api snipplets

* Fri Sep 15 2006 Chris Chabot <chabotc@xs4all.nl> - 3.0.12-5
- Updated to new upstream version

* Mon Sep 11 2006 Chris Chabot <chabotc@xs4all.nl> - 3.0.10-5
- FC6 rebuild

* Sun Aug 13 2006 Chris Chabot <chabotc@xs4all.nl> - 3.0.10-4
- FC6T2 rebuild

* Mon Jun 19 2006 - Chris Chabot <chabotc@xs4all.nl> - 3.0.10-3
- Renamed to php-pecl-apc and added provides php-apc
- Removed php version string from the package version

* Mon Jun 19 2006 - Chris Chabot <chabotc@xs4all.nl> - 3.0.10-2
- Trimmed down BuildRequires
- Added Provices php-pecl(apc)

* Sun Jun 18 2006 - Chris Chabot <chabotc@xs4all.nl> - 3.0.10-1
- Initial package, templated on already existing php-json
  and php-eaccelerator packages
