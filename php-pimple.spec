#
# Fedora spec file for php-pimple
#
# Copyright (c) 2015 Shawn Iwinski <shawn.iwinski@gmail.com>
#
# License: MIT
# http://opensource.org/licenses/MIT
#
# Please preserve changelog entries
#

%global github_owner     silexphp
%global github_name      Pimple
%global github_version   3.0.2
%global github_commit    a30f7d6e57565a2e1a316e1baf2a483f788b258a

%if "%{php_version}" < "7"
%global with_ext 1
%else
%global with_ext 0
BuildArch: noarch
%endif

# Lib
%global composer_vendor  pimple
%global composer_project pimple

%if %{with_ext}
# Ext
%global ext_name pimple
%global with_zts 0%{?__ztsphp:1}
%if "%{php_version}" < "5.6"
%global ini_name %{ext_name}.ini
%else
%global ini_name 40-%{ext_name}.ini
%endif
%endif

# "php": ">=5.3.0"
%global php_min_ver 5.3.0

# Build using "--without tests" to disable tests
%global with_tests  %{?_without_tests:0}%{!?_without_tests:1}

%{!?php_inidir:  %global php_inidir  %{_sysconfdir}/php.d}
%{!?phpdir:      %global phpdir      %{_datadir}/php}

Name:          php-%{composer_project}
Version:       %{github_version}
Release:       7%{?dist}
Summary:       A simple dependency injection container for PHP (extension)

Group:         Development/Libraries
License:       MIT
URL:           http://pimple.sensiolabs.org
Source0:       https://github.com/%{github_owner}/%{github_name}/archive/%{github_commit}/%{name}-%{github_version}-%{github_commit}.tar.gz

BuildRequires: php-devel >= %{php_min_ver}
%if %{with_tests}
# For tests
## composer.json
BuildRequires: %{_bindir}/phpunit
## phpcompatinfo (computed from version 3.0.2)
BuildRequires: php-reflection
BuildRequires: php-spl
%endif

%if %{with_ext}
Requires:      php(zend-abi) = %{php_zend_api}
Requires:      php(api)      = %{php_core_api}
%endif

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter shared private
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif

%description
%{summary}.

NOTE: This package installs the Pimple EXTENSION.

# ------------------------------------------------------------------------------

%package lib

Summary:   A simple dependency injection container for PHP (library)

BuildArch: noarch

# composer.json
Requires:  php(language) >= %{php_min_ver}
# phpcompatinfo (computed from version 3.0.2)
Requires:  php-spl

# Composer
Provides:  php-composer(%{composer_vendor}/%{composer_project}) = %{version}
# Rename
Obsoletes: php-Pimple < %{version}-%{release}
Provides:  php-Pimple = %{version}-%{release}

%description lib
%{summary}.

NOTE: This package installs the Pimple LIBRARY. If you would like the EXTENSION
for improved speed, install "%{name}".

# ------------------------------------------------------------------------------

%prep
%setup -qn %{github_name}-%{github_commit}

: Library: Create autoloader
cat <<'AUTOLOAD' | tee src/Pimple/autoload.php
<?php
/**
 * Autoloader for %{name}-lib and its' dependencies
 *
 * Created by %{name}-lib-%{version}-%{release}
 *
 * @return \Symfony\Component\ClassLoader\ClassLoader
 */

if (!isset($fedoraClassLoader) || !($fedoraClassLoader instanceof \Symfony\Component\ClassLoader\ClassLoader)) {
    if (!class_exists('Symfony\\Component\\ClassLoader\\ClassLoader', false)) {
        require_once '%{phpdir}/Symfony/Component/ClassLoader/ClassLoader.php';
    }

    $fedoraClassLoader = new \Symfony\Component\ClassLoader\ClassLoader();
    $fedoraClassLoader->register();
}

$fedoraClassLoader->addPrefix('Pimple\\', dirname(__DIR__));

return $fedoraClassLoader;
AUTOLOAD

%if %{with_ext}
: Extension: NTS
mv ext/%{ext_name} ext/NTS
%if %{with_zts}
: Extension: ZTS
cp -pr ext/NTS ext/ZTS
%endif

: Extension: Create configuration file
cat << 'INI' | tee %{ini_name}
; Enable %{ext_name} extension
extension=%{ext_name}.so
INI
%endif


%build
%if %{with_ext}
: Extension: NTS
pushd ext/NTS
    %{_bindir}/phpize
    %configure --with-php-config=%{_bindir}/php-config
    make %{?_smp_mflags}
popd
%if %{with_zts}
: Extension: ZTS
pushd ext/ZTS
    %{_bindir}/zts-phpize
    %configure --with-php-config=%{_bindir}/zts-php-config
    make %{?_smp_mflags}
popd
%endif
%endif


%install
: Library
mkdir -p %{buildroot}/%{phpdir}/
cp -rp src/* %{buildroot}/%{phpdir}/

%if %{with_ext}
: Extension: NTS
make -C ext/NTS install INSTALL_ROOT=%{buildroot}
install -D -m 0644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}
%if %{with_zts}
: Extension: ZTS
make -C ext/ZTS install INSTALL_ROOT=%{buildroot}
install -D -m 0644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif
%endif


%check
%if %{with_ext}
: Extension: NTS minimal load test
%{__php} --no-php-ini \
    --define extension=ext/NTS/modules/%{ext_name}.so \
    --modules | grep %{ext_name}

%if %{with_zts}
: Extension: ZTS minimal load test
%{__ztsphp} --no-php-ini \
    --define extension=ext/ZTS/modules/%{ext_name}.so \
    --modules | grep %{ext_name}
%endif
%endif

%if %{with_tests}
: Library: Test suite without extension
%{_bindir}/phpunit --verbose \
    --bootstrap %{buildroot}/%{phpdir}/Pimple/autoload.php

%if %{with_ext}
: Library: Test suite with extension
%{_bindir}/php --define extension=ext/NTS/modules/%{ext_name}.so \
    %{_bindir}/phpunit --verbose \
        --bootstrap %{buildroot}/%{phpdir}/Pimple/autoload.php

: Extension: NTS test suite
pushd ext/NTS
    make test NO_INTERACTION=1 REPORT_EXIT_STATUS=1
popd

%if %{with_zts}
: Extension: ZTS test suite
pushd ext/ZTS
    make test NO_INTERACTION=1 REPORT_EXIT_STATUS=1
popd
%endif
%endif
%else
: Tests skipped
%endif


%{!?_licensedir:%global license %%doc}

%files
%license LICENSE
%doc CHANGELOG
%doc README.rst
%if %{with_ext}
# NTS
%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{ext_name}.so
# ZTS
%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{ext_name}.so
%endif
%endif

%files lib
%license LICENSE
%doc CHANGELOG
%doc README.rst
%doc composer.json
%{phpdir}/Pimple
%exclude %{phpdir}/Pimple/Tests


%changelog
* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jul 07 2017 Igor Gnatenko <ignatenko@redhat.com> - 3.0.2-5
- Rebuild due to bug in RPM (RHBZ #1468476)

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Jun 27 2016 Remi Collet <remi@fedoraproject.org> - 3.0.2-3
- disable the extension with PHP 7

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sat Sep 12 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 3.0.2-1
- Updated to 3.0.2 (RHBZ #1262507)

* Sun Aug 02 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 3.0.1-1
- Updated to 3.0.1

* Mon Jul 20 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 3.0.0-5
- Autoloader changed to Symfony ClassLoader

* Thu May 21 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 3.0.0-4
- Add library autoloader
- Spec cleanup

* Wed Sep 03 2014 Shawn Iwinski <shawn.iwinski@gmail.com> - 3.0.0-3
- Separate extension and library (i.e. sub-package library)

* Mon Aug 25 2014 Shawn Iwinski <shawn.iwinski@gmail.com> - 3.0.0-2
- Fixed compat file location in description
- Included real class in compat file
- Always run extension minimal load test
- Fixed test suite with previous installed version
- "make test NO_INTERACTION=1 REPORT_EXIT_STATUS=1" instead of "echo "n" | make test"

* Thu Jul 31 2014 Shawn Iwinski <shawn.iwinski@gmail.com> - 3.0.0-1
- Updated to 3.0.0
- Added custom compat file for obsoleted php-Pimple

* Tue Jul 29 2014 Shawn Iwinski <shawn.iwinski@gmail.com> - 2.1.1-1
- Initial package
