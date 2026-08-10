#!/usr/bin/env node
/**
 * HarnessWiki 기계 검증 스크립트 (Lint)
 *
 * 검증 항목:
 * 1. Frontmatter 유효성 (YAML 포맷)
 * 2. 스키마 구조 검증 (경로, 파일명)
 * 3. 파일명 규칙 (kebab-case)
 * 4. 링크 검증 (존재 여부, 경로 깊이)
 */

import fs from 'fs';
import path from 'path';
import { globSync } from 'glob';
import yaml from 'js-yaml';

interface ValidationResult {
  errors: string[];
  warnings: string[];
  info: string[];
}

class WikiLinter {
  private wikiRoot: string;
  private errors: string[] = [];
  private warnings: string[] = [];
  private info: string[] = [];

  constructor(wikiRoot: string = '.') {
    this.wikiRoot = wikiRoot;
  }

  private logError(filePath: string, message: string): void {
    this.errors.push(`[ERROR] ${filePath}: ${message}`);
  }

  private logWarning(filePath: string, message: string): void {
    this.warnings.push(`[WARN]  ${filePath}: ${message}`);
  }

  private logInfo(filePath: string, message: string): void {
    this.info.push(`[INFO]  ${filePath}: ${message}`);
  }

  private isKebabCase(text: string): boolean {
    /**
     * 슬러그가 kebab-case 형식인지 확인
     * 허용: 소문자, 숫자, 하이픈, 한글, 기타 유니코드 문자
     */
    if (!text || text.startsWith('-') || text.endsWith('-')) {
      return false;
    }

    // 한글 포함 확인
    const koreanRegex = /[가-힯]/;
    if (koreanRegex.test(text)) {
      return true; // 한글은 허용
    }

    // 영문+숫자+하이픈만 허용
    return /^[a-z0-9-]+$/.test(text);
  }

  private validateFrontmatter(filePath: string): void {
    try {
      const content = fs.readFileSync(filePath, 'utf-8');

      if (content.startsWith('---')) {
        const endIndex = content.indexOf('---', 3);
        if (endIndex !== -1) {
          const frontmatterText = content.substring(3, endIndex).trim();
          try {
            yaml.load(frontmatterText);
            this.logInfo(filePath, 'Frontmatter 유효');
          } catch (e) {
            const error = e as Error;
            this.logError(
              filePath,
              `Frontmatter YAML 문법 오류: ${error.message.substring(0, 100)}`
            );
          }
        } else {
          this.logError(filePath, 'Frontmatter 닫는 --- 없음');
        }
      }
    } catch (e) {
      const error = e as Error;
      this.logError(filePath, `파일 읽기 오류: ${error.message}`);
    }
  }

  private validateMetaStructure(metaFile: string): void {
    try {
      const content = fs.readFileSync(metaFile, 'utf-8');

      const requiredSections = ['## 메타정보', '## 한줄 요약'];
      for (const section of requiredSections) {
        if (!content.includes(section)) {
          this.logWarning(metaFile, `필수 섹션 '${section}' 없음`);
        }
      }
    } catch (e) {
      const error = e as Error;
      this.logError(metaFile, `검증 오류: ${error.message}`);
    }
  }

  private resolvePath(basePath: string, relativePath: string): string {
    /**
     * 상대경로를 절대경로로 변환
     */
    const parts = relativePath.replace(/\\/g, '/').split('/');
    let current = basePath;

    for (const part of parts) {
      if (part === '..') {
        current = path.dirname(current);
      } else if (part && part !== '.') {
        current = path.join(current, part);
      }
    }

    return current;
  }

  private validateTopicLinks(topicFile: string, slug: string): void {
    try {
      const content = fs.readFileSync(topicFile, 'utf-8');

      // 링크 추출: [text](path)
      const linkPattern = /\[([^\]]+)\]\(([^)]+)\)/g;
      let match;

      while ((match = linkPattern.exec(content)) !== null) {
        const linkPath = match[2];

        // 상대경로 링크만 검증
        if (!linkPath.startsWith('http')) {
          const normalizedPath = linkPath.replace(/\\/g, '/');
          const baseDir = path.dirname(topicFile);
          const fullPath = this.resolvePath(baseDir, normalizedPath);

          // 경로 깊이 검증
          if (normalizedPath.startsWith('../../../raw/')) {
            // raw 참조는 3단계 깊이 OK
          } else if (normalizedPath.startsWith('../')) {
            // 형제 토픽 링크
            const upLevelCount = (normalizedPath.match(/\.\.\//g) || []).length;
            if (upLevelCount !== 1) {
              this.logError(
                topicFile,
                `형제 토픽 링크 깊이 오류: ${linkPath}`
              );
            }
          } else if (normalizedPath.startsWith('../../')) {
            // 다른 경로 (e.g., 결정.md)
          } else {
            this.logWarning(
              topicFile,
              `예상치 못한 링크 경로: ${linkPath}`
            );
          }

          // 파일 존재 여부 확인
          if (!normalizedPath.includes('raw/') && !fs.existsSync(fullPath)) {
            this.logError(topicFile, `링크가 가리키는 파일 없음: ${linkPath}`);
          }
        }
      }
    } catch (e) {
      const error = e as Error;
      this.logError(topicFile, `링크 검증 오류: ${error.message}`);
    }
  }

  private validateRawStructure(): void {
    const rawDir = path.join(this.wikiRoot, 'raw');

    if (!fs.existsSync(rawDir)) {
      this.logWarning('raw/', '디렉토리가 없음');
      return;
    }

    const folders = fs.readdirSync(rawDir);

    for (const folder of folders) {
      const folderPath = path.join(rawDir, folder);

      if (!fs.statSync(folderPath).isDirectory()) {
        continue;
      }

      // YYYY-MM-DD_슬러그 형식 검증
      const match = /^(\d{4})-(\d{2})-(\d{2})_(.+)$/.exec(folder);
      if (!match) {
        this.logError(
          `raw/${folder}`,
          '폴더명 형식 오류: YYYY-MM-DD_슬러그 형식 필요'
        );
        continue;
      }

      const slug = match[4];
      if (!this.isKebabCase(slug)) {
        this.logError(
          `raw/${folder}`,
          `슬러그 '${slug}'가 kebab-case 아님 (허용: 소문자, 숫자, 하이픈, 한글)`
        );
      }

      // raw.md, meta.md 존재 확인
      const rawFile = path.join(folderPath, 'raw.md');
      const metaFile = path.join(folderPath, 'meta.md');

      if (!fs.existsSync(rawFile)) {
        this.logError(`raw/${folder}`, 'raw.md 파일 없음');
      } else {
        this.validateFrontmatter(rawFile);
      }

      if (!fs.existsSync(metaFile)) {
        this.logError(`raw/${folder}`, 'meta.md 파일 없음');
      } else {
        this.validateFrontmatter(metaFile);
        this.validateMetaStructure(metaFile);
      }
    }
  }

  private validateTopicStructure(): void {
    const 주제Dir = path.join(this.wikiRoot, 'wiki', '주제');

    if (!fs.existsSync(주제Dir)) {
      this.logWarning('wiki/주제/', '디렉토리가 없음');
      return;
    }

    const folders = fs.readdirSync(주제Dir);

    for (const folder of folders) {
      const folderPath = path.join(주제Dir, folder);

      if (!fs.statSync(folderPath).isDirectory()) {
        continue;
      }

      const slug = folder;
      if (!this.isKebabCase(slug)) {
        this.logError(`wiki/주제/${slug}`, '슬러그가 kebab-case 아님');
      }

      // 폴더 노트 구조 검증: wiki/주제/슬러그/슬러그.md
      const expectedFile = path.join(folderPath, `${slug}.md`);
      if (!fs.existsSync(expectedFile)) {
        this.logError(
          `wiki/주제/${slug}`,
          `파일 '${slug}.md' 없음 (폴더 노트 구조 필요)`
        );
      } else {
        this.validateFrontmatter(expectedFile);
        this.validateTopicLinks(expectedFile, slug);
      }

      // 파일이 폴더명과 다르면 경고
      const files = fs.readdirSync(folderPath);
      for (const file of files) {
        if (file.endsWith('.md') && file !== `${slug}.md` && file !== 'index.md') {
          this.logWarning(
            `wiki/주제/${slug}/${file}`,
            '폴더명과 일치하지 않는 파일명'
          );
        }
      }
    }
  }

  private validateRollupFiles(): void {
    const filesToCheck = [
      path.join(this.wikiRoot, 'wiki', '결정', '결정.md'),
      path.join(this.wikiRoot, 'wiki', '액션아이템', '액션아이템.md'),
    ];

    for (const filePath of filesToCheck) {
      if (!fs.existsSync(filePath)) {
        this.logWarning(filePath, '파일 없음');
        continue;
      }

      this.validateFrontmatter(filePath);

      // 링크 검증
      try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const linkPattern = /\[([^\]]+)\]\(([^)]+)\)/g;
        let match;

        while ((match = linkPattern.exec(content)) !== null) {
          const linkPath = match[2];

          if (!linkPath.startsWith('http')) {
            const normalizedPath = linkPath.replace(/\\/g, '/');
            const baseDir = path.dirname(filePath);
            const fullPath = this.resolvePath(baseDir, normalizedPath);

            if (!fs.existsSync(fullPath)) {
              this.logError(filePath, `깨진 링크: ${linkPath}`);
            }
          }
        }
      } catch (e) {
        const error = e as Error;
        this.logError(filePath, `검증 오류: ${error.message}`);
      }
    }
  }

  private validateIndex(): void {
    const indexFile = path.join(this.wikiRoot, 'wiki', 'index.md');

    if (!fs.existsSync(indexFile)) {
      this.logError('wiki/index.md', '파일 없음');
      return;
    }

    // 토픽 폴더와 index의 링크 일치 확인
    const 주제Dir = path.join(this.wikiRoot, 'wiki', '주제');
    if (fs.existsSync(주제Dir)) {
      const 주제 = fs
        .readdirSync(주제Dir)
        .filter((f) => fs.statSync(path.join(주제Dir, f)).isDirectory());

      try {
        const content = fs.readFileSync(indexFile, 'utf-8');

        for (const topic of 주제) {
          // index에 해당 토픽이 링크되어 있는지 확인
          if (!content.includes(`주제/${topic}/`)) {
            this.logWarning(
              'wiki/index.md',
              `토픽 '${topic}'이 index에 없음 (고아 페이지)`
            );
          }
        }
      } catch (e) {
        const error = e as Error;
        this.logError('wiki/index.md', `검증 오류: ${error.message}`);
      }
    }
  }

  public run(): number {
    console.log('[LINT] HarnessWiki 기계 검증 시작...\n');

    this.validateRawStructure();
    this.validateTopicStructure();
    this.validateRollupFiles();
    this.validateIndex();

    // 결과 출력
    console.log('\n' + '='.repeat(60));
    console.log('검증 완료');
    console.log('='.repeat(60) + '\n');

    if (this.errors.length > 0) {
      console.log(`[ERROR] 오류 (${this.errors.length}건):`);
      for (const error of this.errors) {
        console.log(`  ${error}`);
      }
      console.log();
    }

    if (this.warnings.length > 0) {
      console.log(`[WARN] 경고 (${this.warnings.length}건):`);
      for (const warning of this.warnings) {
        console.log(`  ${warning}`);
      }
      console.log();
    }

    if (this.info.length > 0) {
      console.log(`[INFO] 정보 (${this.info.length}건):`);
      const displayCount = Math.min(5, this.info.length);
      for (let i = 0; i < displayCount; i++) {
        console.log(`  ${this.info[i]}`);
      }
      if (this.info.length > 5) {
        console.log(`  ... 외 ${this.info.length - 5}건`);
      }
      console.log();
    }

    // 요약
    console.log('[SUMMARY]');
    console.log(`  - 오류: ${this.errors.length}건`);
    console.log(`  - 경고: ${this.warnings.length}건`);
    console.log(`  - 정보: ${this.info.length}건`);

    // 종료 코드
    return this.errors.length > 0 ? 1 : 0;
  }
}

// 실행
const args = process.argv.slice(2);
const wikiRoot = args[0] || '.';
const linter = new WikiLinter(wikiRoot);
process.exit(linter.run());
