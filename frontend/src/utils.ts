export function normalizeFileUrl(url: string): string {
  return url.replace('http://minio:9000', 'http://localhost:9000')
}
