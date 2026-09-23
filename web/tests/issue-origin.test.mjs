import assert from 'node:assert/strict'
import test from 'node:test'
import { cachedIssueTime, isSupportedCachedIssue, nextCachedIssue, replayDates } from '../src/lib/time.ts'

test('both horizons use the supported 12Z origin; other hours and sub-hours are rejected', () => {
  for (const horizon of [24, 48]) {
    const request = { issue_time: cachedIssueTime('2026-01-31'), horizon_hours: horizon }
    assert.equal(new Date(request.issue_time).toISOString(), '2026-01-31T12:00:00.000Z')
    assert.equal(isSupportedCachedIssue(request.issue_time), true)
  }
  for (const issue of ['2026-01-31T11:00:00Z', '2026-01-31T13:00:00Z', '2026-01-31T12:01:00Z', 'invalid']) {
    assert.equal(isSupportedCachedIssue(issue), false)
    assert.equal(nextCachedIssue(issue), null)
  }
})

test('29 replay origins and +24h updates agree, including the February boundary', () => {
  const dates = replayDates()
  assert.equal(dates.length, 29)
  for (let i = 0; i < dates.length; i++) {
    const issue = cachedIssueTime(dates[i])
    assert.equal(isSupportedCachedIssue(issue), true)
    assert.equal(nextCachedIssue(issue), i + 1 < dates.length ? new Date(cachedIssueTime(dates[i + 1])).toISOString() : null)
  }
  assert.equal(isSupportedCachedIssue('2026-01-30T12:00:00Z'), false)
  assert.equal(isSupportedCachedIssue('2026-03-01T12:00:00Z'), false)
})
