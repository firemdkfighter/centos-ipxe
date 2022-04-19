# debugging firmwares does not go the same way as a normal program.
# moreover, all architectures providing debuginfo for a single noarch
# package is currently clashing in koji, so don't bother.
%global debug_package %{nil}

Name:    ipxe-opentech
Version: 1.21.1
Release: 1%{?dist}
Summary:   X86 Network boot loader images in bootable USB, CD, floppy and GRUB formats

Group:   System Environment/Base
License: GPLv2 with additional permissions and BSD
URL:     http://ipxe.org/
Source0: https://github.com/ipxe/ipxe/archive/refs/tags/v%{version}.tar.gz

# Enable IPv6 for qemu's config
# Sent upstream: http://lists.ipxe.org/pipermail/ipxe-devel/2015-November/004494.html
Patch01: ipxe.patch

BuildRequires: perl-interpreter
BuildRequires: perl-Getopt-Long
BuildRequires: mtools
BuildRequires: mkisofs
BuildRequires: xz-devel
BuildRequires: binutils-devel
BuildRequires: gcc
BuildRequires: syslinux
BuildArch: noarch

Provides:  ipxe-bootimgs = %{version}-%{release}
Obsoletes: ipxe-bootimgs < 20181214-9.git133f4c47
Obsoletes: gpxe <= 1.0.1
Obsoletes: gpxe-bootimgs <= 1.0.1

%description
iPXE is an open source network bootloader. It provides a direct
replacement for proprietary PXE ROMs, with many extra features such as
DNS, HTTP, iSCSI, etc.

This package contains the iPXE boot images in USB, CD, floppy, and PXE
UNDI formats.

%prep
%setup -qn ipxe-%{version}
%autopatch -p1
pushd src
# ath9k drivers are too big for an Option ROM, and ipxe devs say it doesn't
# make sense anyways
# http://lists.ipxe.org/pipermail/ipxe-devel/2012-March/001290.html
rm -rf drivers/net/ath/ath9k
popd

%build
cd src

make_ipxe() {
    make %{?_smp_mflags} \
        NO_WERROR=1 V=1 \
        "$@"
}

make_ipxe bin-i386-efi/ipxe.efi bin-x86_64-efi/ipxe.efi \
    bin-x86_64-efi/snponly.efi

make_ipxe ISOLINUX_BIN=/usr/share/syslinux/isolinux.bin \
    bin/undionly.kpxe bin/ipxe.{dsk,iso,usb,lkrn}

%install
mkdir -p %{buildroot}/%{_datadir}/ipxe/
mkdir -p %{buildroot}/%{_datadir}/ipxe.efi/
pushd src/bin/

cp -a undionly.kpxe ipxe.{iso,usb,dsk,lkrn} %{buildroot}/%{_datadir}/ipxe/
popd

cp -a src/bin-i386-efi/ipxe.efi %{buildroot}/%{_datadir}/ipxe/ipxe-i386.efi
cp -a src/bin-x86_64-efi/ipxe.efi %{buildroot}/%{_datadir}/ipxe/ipxe-x86_64.efi
cp -a src/bin-x86_64-efi/ipxe-rhcert.efi %{buildroot}/%{_datadir}/ipxe/ipxe-x86_64-rhcert.efi
cp -a src/bin-x86_64-efi/snponly.efi %{buildroot}/%{_datadir}/ipxe/ipxe-snponly-x86_64.efi

%files
%dir %{_datadir}/ipxe
%{_datadir}/ipxe/ipxe.iso
%{_datadir}/ipxe/ipxe.usb
%{_datadir}/ipxe/ipxe.dsk
%{_datadir}/ipxe/ipxe.lkrn
%{_datadir}/ipxe/ipxe-i386.efi
%{_datadir}/ipxe/ipxe-x86_64.efi
%{_datadir}/ipxe/undionly.kpxe
%{_datadir}/ipxe/ipxe-snponly-x86_64.efi
%doc COPYING COPYING.GPLv2 COPYING.UBDL
