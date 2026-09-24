---
# ==============================================================================
# METADATA DOKUMEN & COVER
# ==============================================================================
title: "Buku Panduan Standar Template"
subtitle: "PEDOMAN OPERASIONAL & PENULISAN DOKUMEN"
description: "Panduan Teknis Penulisan Naskah Berbasis Markdown ke LaTeX PENS"
doc_number: "FL-OPS-TMP-ID-001"
version: "1.0.0"
role: "Template ID"
status: "Dokumen Acuan Resmi"
publisher: "Tim Arsitektur & Operasional FoodLAB PENS"
author: "FoodLAB - PENS"
edition: "Edisi Pertama"
year: "2026"
city: "Surabaya, Indonesia"
institution: "Politeknik Elektronika Negeri Surabaya (PENS)"
system: "SISTEM INFORMASI OPERASIONAL DIGITAL KAMPUS"
department: "Laboratorium Rekayasa Perangkat Lunak & Sistem Cerdas"

# ==============================================================================
# METADATA PDF (Properties File PDF & Hyperref)
# ==============================================================================
pdf_title: "Buku Panduan Template FoodLAB PENS"
pdf_subject: "Panduan Operasional Standar Penulisan Naskah FL-OPS-TMP-ID-001"
pdf_keywords: "FoodLAB, Template, Guidebook, PENS, SOP, Panduan"
pdf_author: "FoodLAB - PENS"

# ==============================================================================
# PENGATURAN TATA LETAK & VISUAL
# ==============================================================================
template: true
lang: "id"
enable_chapter_cover: "true"
---

# Kata Pengantar

Kata pengantar ini secara otomatis diekstrak oleh program ke dalam bagian *frontmatter* dokumen LaTeX dengan penomoran halaman standar terpadu. Tuliskan latar belakang penyusunan dokumen, sasaran pembaca, dan ucapan terima kasih dalam satu hingga tiga paragraf padat.

Semua dokumen disusun menggunakan satu file sumber Markdown mandiri di dalam folder `content/`. Pengguna tidak perlu menyunting konfigurasi LaTeX secara terpisah karena seluruh parameter telah ditentukan melalui frontmatter YAML di atas.

---

# Bab 1: Struktur Hierarki Heading dan Penomoran

## 1.1 Standar Hierarki Bab dan Subbab

Program konverter memetakan hierarki heading Markdown secara cerdas agar tidak terjadi duplikasi penomoran:

- `# Bab <N>: <Judul>` dipetakan sebagai bab utama (`\chapter`). Jika `enable_chapter_cover` bernilai `true`, halaman pemisah bab (*chapter divider cover*) satu halaman penuh dengan aksen garis biru-emas dan logo resmi akan digenerasi otomatis sebelum isi bab dimulai.
- `## <Judul Subbab>` atau `## <N.M> <Judul>` dipetakan sebagai subbab (`\section`). LaTeX akan memberikan nomor urut otomatis seperti `1.1 Judul` tanpa pengulangan angka ganda.
- `### <Judul Sub-subbab>` atau `### <N.M.P> <Judul>` dipetakan sebagai sub-subbab (`\subsection`).

> **Penting**
>
> Anda dapat menulis judul subbab secara langsung seperti `## Sejarah FoodLAB` maupun menyertakan nomor manual seperti `## 1.1 Sejarah FoodLAB`. Program secara otomatis mendeteksi dan menormalkan penomoran sehingga keluaran judul selalu rapi.

## 1.2 Format Tipografi Teks

Gunakan sintaks Markdown standar untuk penekanan teks:

- **Teks Tebal**: Menggunakan dua tanda bintang `**teks tebal**` untuk penegasan kata kunci atau entitas penting.
- *Teks Miring*: Menggunakan satu tanda bintang `*istilah asing*` untuk istilah operasional non-Indonesia.
- `Kode / Identitas`: Menggunakan tanda petik satu miring `` `FL-ORDER-001` `` untuk kode referensi atau sintaks.
- Tautan Internal: Gunakan `[Teks Rujukan](#anchor-judul)` yang otomatis menjadi tautan interaktif PDF.

## 1.3 Kotak Informasi dan Peringatan Lapangan

Untuk membuat kotak SOP, peringatan, atau catatan khusus lapangan, gunakan sintaks blockquote Markdown (`>`) dengan judul tebal pada baris pertama:

> **Pilar Nilai Pelayanan Pengantaran**
>
> - **Efisiensi**: Setiap pesanan diantar dengan cepat dan tepat sasaran.
> - **Keutuhan**: Makanan dan minuman sampai ke tangan konsumen dalam kondisi sama seperti saat diserahkan tenant.

Kotak ini akan otomatis di-render dengan bingkai garis putus-putus (*dashed*) berwarna emas dan latar belakang krem hangat sesuai standar resmi FoodLAB.

## 1.4 Simbol, Karakter Khusus, dan Tautan Antar-Bab

- **Karakter Khusus**: Karakter seperti `&`, `%`, `$`, `#`, `_` otomatis di-escape oleh parser.
- **Tanda Panah & Alur**: Gunakan teks standar seperti `->` atau `>` (contoh: `Masuk -> Siap Diantar -> Diantar`) tanpa perlu menulis sintaks matematika LaTeX manual.
- **Tautan Internal**: Gunakan format `[Teks Tautan](#anchor-slug)` untuk merujuk ke bab/subbab lain (contoh: `[Bab 2.1](#21-format-tabel-data)`). Tautan akan aktif dan dapat diklik pada dokumen PDF.

---

# Bab 2: Format Tabel, Gambar, dan Daftar

## 2.1 Format Tabel Data

Tabel data disusun menggunakan tabel pipa Markdown standar. Program mengonversinya menjadi tabel `tabularx` LaTeX dengan lebar penuh dan garis horizontal standar akademik:

| Parameter YAML | Wajib/Opsional | Deskripsi Fungsi |
| --- | --- | --- |
| title | Wajib | Judul dokumen yang ditampilkan pada cover |
| subtitle | Wajib | Subjudul dokumen dalam huruf kapital biru |
| doc_number | Wajib | Nomor identitas dokumen operasional kampus |
| version | Wajib | Versi rilis dokumen (contoh: 0.2.8) |
| pdf_title | Opsional | Judul yang muncul pada title bar pembaca PDF |
| pdf_keywords | Opsional | Kata kunci untuk indexing pencarian PDF |

## 2.2 Daftar Poin Berurutan dan Tidak Berurutan

Daftar poin tidak berurutan menggunakan tanda strip `-`:

- Pemeriksaan integritas kemasan pesanan di stan kantin.
- Konfirmasi penjemputan pada aplikasi mobile.
- Pengantaran ke titik serah terima gedung tujuan.

Daftar berurutan menggunakan penomoran angka `1.`:

1. Buka aplikasi dan aktifkan status kerja operasional.
2. Terima notifikasi penawaran pesanan terdekat.
3. Lakukan verifikasi kode serah terima bersama mitra tenant.

## 2.3 Format Gambar, Tangkapan Layar (Screenshot), dan Penjelasan

Untuk menyisipkan gambar atau tangkapan layar antarmuka aplikasi, letakkan file gambar di dalam folder `figures/` (misal: `figures/logo-pens.png`), lalu gunakan sintaks gambar Markdown dengan teks caption:

![Logo Resmi Institusi PENS](figures/logo-pens.png)

*Gambar di atas merupakan contoh penyisipan aset grafis atau tangkapan layar antarmuka aplikasi. Keterangan teks di bawah gambar ini dapat digunakan untuk memberikan penjelasan mendalam terkait alur fitur atau elemen UI yang ditampilkan.*
