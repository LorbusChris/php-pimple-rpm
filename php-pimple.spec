#
# Fedora spec file for php-pimple
#
# Copyright (c) 2015-2017 Shawn Iwinski <shawn.iwinski@gmail.com>
#
# License: MIT
# http://opensource.org/licenses/MIT
#
# Please preserve changelog entries
#

%global github_owner     silexphp
%global github_name      Pimple
%global github_version   3.2.2
%global github_commit    4d45fb62d96418396ec58ba76e6f065bca16e10a

%global composer_vendor  pimple
%global composer_project pimple

# "php": ">=5.3.0"
%global php_min_ver 5.3.0
# "psr/container": "^1.0"
%global psr_container_min_ver 1.0
%global psr_container_max_ver 2.0

# Build using "--without tests" to disable tests
%global with_tests  %{?_without_tests:0}%{!?_without_tests:1}

%{!?phpdir:  %global phpdir  %{_datadir}/php}

Name:          php-%{composer_project}
Version:       %{github_version}
Release:       1%{?dist}
Summary:       A simple dependency injection container for PHP

Group:         Development/Libraries
License:       MIT
URL:           http://pimple.sensiolabs.org
Source0:       https://github.com/%{github_owner}/%{github_name}/archive/%{github_commit}/%{name}-%{github_version}-%{github_commit}.tar.gz

BuildArch:     noarch
# Tests
%if %{with_tests}
## composer.json
BuildRequires: php-composer(phpunit/phpunit)
BuildRequires: php-composer(psr/container) <  %{psr_container_max_ver}
BuildRequires: php-composer(psr/container) >= %{psr_container_min_ver}
## phpcompatinfo (computed from version 3.2.2)
BuildRequires: php-reflection
BuildRequires: php-spl
## Autoloader
BuildRequires: php-composer(fedora/autoloader)
%endif

# composer.json
Requires:  php(language) >= %{php_min_ver}
Requires:  php-composer(psr/container) <  %{psr_container_max_ver}
Requires:  php-composer(psr/container) >= %{psr_container_min_ver}
# phpcompatinfo (computed from version 3.2.2)
Requires:  php-spl
## Autoloader
Requires:  php-composer(fedora/autoloader)

# Composer
Provides:  php-composer(%{composer_vendor}/%{composer_project}) = %{version}
# Rename
Obsoletes: php-Pimple < %{version}-%{release}
Provides:  php-Pimple = %{version}-%{release}
# Drop extension
Obsoletes: php-pimple-lib < %{version}-%{release}
Provides:  php-pimple-lib = %{version}-%{release}

%description
%{summary}.

Autoloader: %{phpdir}/Pimple/autoload.php


%prep
%setup -qn %{github_name}-%{github_commit}


%build
: Create autoloader
cat <<'AUTOLOAD' | tee src/Pimple/autoload.php
<?php
/**
 * Autoloader for %{name} and its' dependencies
 * (created by %{name}-%{version}-%{release}).
 */
require_once '%{phpdir}/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('Pimple\\', __DIR__);

\Fedora\Autoloader\Dependencies::required(array(
    '%{phpdir}/Psr/Container/autoload.php',
));
AUTOLOAD


%install
mkdir -p %{buildroot}/%{phpdir}/
cp -rp src/Pimple %{buildroot}/%{phpdir}/


%check
%if %{with_tests}
: Upstream tests
RETURN_CODE=0
PHPUNIT=$(which phpunit)
for PHP_EXEC in "" %{?rhel:php54 php55} php56 php70 php71 php72; do
    if [ -z "$PHP_EXEC" ] || which $PHP_EXEC; then
        $PHP_EXEC $PHPUNIT --verbose \
            --bootstrap %{buildroot}/%{phpdir}/Pimple/autoload.php \
            || RETURN_CODE=1
    fi
done
exit $RETURN_CODE
%else
: Tests skipped
%endif


%files
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc CHANGELOG
%doc README.rst
%doc composer.json
%{phpdir}/Pimple
%exclude %{phpdir}/Pimple/Tests


%changelog
* Sat Aug 05 2017 Shawn Iwinski <shawn.iwinski@gmail.com> - 3.2.2-1
- Update to 3.2.2 (RHBZ #1467881)
- Drop extension completely
- Switch autoloader to php-composer(fedora/autoloader)
- Test with SCLs if available

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
