# Third-party notices

The root MIT licence covers CleanFrame's original code and documentation. Third-party material retains the terms below. Keep these notices and the adjacent licence texts when sharing source or a build.

## Fonts

| Material | Terms and source record |
| --- | --- |
| Manrope | SIL Open Font License 1.1; `assets/manrope-OFL.txt` |
| Geist and Newsreader | SIL Open Font License 1.1; licences beside the files in `assets/fonts/`, with exact sources and hashes in `assets/fonts/SOURCES.json` |
| Optional PP Neue Montreal, PP Mori and PP Pangram Sans | Proprietary. Binaries stay in ignored `.local/` storage and are excluded from Git and public exports. The optional local overlay requires the user's own permission to use and embed those files. |

The public app uses Manrope, Geist and Newsreader. A personal widget containing proprietary fonts must stay private. See [Pangram's licensing information](https://pangrampangram.com/pages/eula).

## Icons and trademarks

| Material | Provenance and terms |
| --- | --- |
| Simple Icons service marks | CC0; exact revisions and adaptations in `assets/icons/SOURCES.json` and `ADDITIONAL-SOURCES.json`. The CC0 text is retained beside the icons. |
| Disney+, ABC and SBS marks | [Custom Brand Icons](https://github.com/elax46/custom-brand-icons), MIT. The retained licence is `assets/icons/CUSTOM-BRAND-ICONS-LICENSE.txt`. ABC and SBS sources were replaced during the public-source review. Exact revisions, source files and extraction/recolour notes are in `SOURCES.json`. |
| Art, apps, settings and home outlines | Original CleanFrame drawings, covered by the project's MIT licence. |

Brand marks identify services. Their owners retain trademark rights; this project claims no endorsement or affiliation. The older Australian TV icon archive's GPL text is retained for historical provenance only; no current icon uses that archive.

## Photographs and derived materials

The fifteen photo pages were individually checked on 20 October 2026. Each displayed its credited author and free use under the [Unsplash License](https://unsplash.com/license). The [asset source register](https://github.com/nthnclrk/CleanFrame/blob/fa537d1892b71d2de2bf94c24cbff3812e9f70d5/docs/asset-sources.md) links every page. Runtime paths are in `assets/wallpapers/SOURCES.json`.

Photographers retain their rights. Wallpapers, thumbnails, panel backgrounds and material fields derive from the credited photographs and retain their terms. The Unsplash licence permits copying, modification and distribution subject to its restrictions, including on selling unmodified images and building a competing image service.

## Development dependencies and exports

Development dependencies retain the licences in their npm packages. They are not copied into the TV JavaScript runtime.

The public source export excludes private fonts and includes this notice and the root MIT licence. Preserve the included font and icon licence texts. Review [upstream public release preparation](https://github.com/nthnclrk/CleanFrame/blob/fa537d1892b71d2de2bf94c24cbff3812e9f70d5/docs/public-release.md) before publishing a repository or download.

## Family Home adaptation

RTVE Play, Movistar Plus+ and Plex marks are carried over from the owner’s Family Home 0.4.0 source records and bundled service logos. Live TV is an original outline. RTVE Play is a PD-textlogo from https://commons.wikimedia.org/wiki/File:RTVE_Play_logo.svg (RTVE); Movistar Plus+ uses MIT Custom Brand Icons revision 05fe01c5841e811f7ce73d76dfb6bd7b949328f8, icon-svg/movistar-plus.svg; Plex uses CC0 Simple Icons 11.15.0, icons/plex.svg. Geometry is retained with monochrome coloring. The source fork retains CleanFrame’s MIT license and every original font, icon and wallpaper notice. No proprietary Pangram fonts are included.
