"""Private fixture tests. Stdlib-only; import the application by file path."""

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor


# Keep test execution inside the two-file write contract, including imports.
sys.dont_write_bytecode = True
_SOURCE = (Path(__file__).resolve().parents[1] / ".opencode" / "skills" /
           "core-identity" / "scripts" / "discovery_lab_app.py")
_SPEC = importlib.util.spec_from_file_location("private_discovery_app", _SOURCE)
lab = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(lab)


class FixtureTests(unittest.TestCase):
    def app(self, scenario, vulnerable=False, seed=731):
        return lab.build_app(lab.SCENARIOS[scenario], vulnerable, seed)

    def call(self, app, method, path, body=None, user=0):
        account = app.describe()["accounts"][user]
        result = app.handle(method, path, {} if body is None else body,
                            {"authorization": "Bearer " + account["token"],
                             "content-type": "application/json"})
        self.check_result(result)
        return result

    def check_result(self, result):
        self.assertIs(type(result), tuple)
        self.assertEqual(len(result), 3)
        status, payload, oracle = result
        self.assertIs(type(status), int)
        self.assertIs(type(payload), dict)
        self.assertIs(type(oracle), dict)
        self.assertEqual(set(oracle), {"control", "boundary", "violation", "reason"})
        for flag in ("control", "boundary", "violation"):
            self.assertIs(type(oracle[flag]), bool)
        self.assertIsInstance(oracle["reason"], str)
        self.assertLess(len(oracle["reason"]), 160)
        self.assertLess(len(json.dumps(payload, allow_nan=False)), 16384)
        self.assertTrue(set(payload).isdisjoint({"oracle", "boundary", "violation", "vulnerable"}))

    def flags(self, result, control=False, boundary=False, violation=False):
        self.assertEqual({k: result[2][k] for k in ("control", "boundary", "violation")},
                         {"control": control, "boundary": boundary, "violation": violation})

    def packet(self, app, user=0):
        packets = self.call(app, "GET", "/api/packets?sort=title", user=user)[1]["packets"]
        self.assertEqual(len(packets), 1)
        packet_id = packets[0]["id"]
        revisions = self.call(app, "GET", "/api/packets/" + packet_id + "/revisions", user=user)[1]["revisions"]
        return packet_id, revisions[-1]["id"]

    def preview(self, app, packet, revision, user=0):
        return self.call(app, "POST", "/api/packets/" + packet + "/preview",
                         {"revision_id": revision}, user)

    def booking(self, app, user=0):
        return self.call(app, "GET", "/api/bookings", user=user)[1]["bookings"][0]

    def wallet(self, app, user=0):
        return self.call(app, "GET", "/api/wallet", user=user)[1]["wallet"]["available_credits"]

    def cancel(self, app, booking, key="cancel-1", user=0, reason="plans_changed"):
        return self.call(app, "POST", "/api/bookings/" + booking["id"] + "/cancel",
                         {"reason": reason, "request_key": key}, user)

    def test_factory_and_description_contract(self):
        self.assertIsInstance(lab.SCENARIOS, (tuple, list))
        self.assertEqual(len(set(lab.SCENARIOS)), 2)
        for scenario in range(2):
            a, b = self.app(scenario, True), self.app(scenario, False)
            description = a.describe()
            self.assertEqual(description, b.describe())
            self.assertLess(len(json.dumps(description)), 16384)
            self.assertTrue(description["synthetic"])
            for field in ("product", "description", "routes", "security_rules", "workflow"):
                self.assertTrue(description[field])
            accounts = description["accounts"]
            self.assertEqual(len(accounts), 2)
            for key in ("label", "token"):
                self.assertEqual(len({account[key] for account in accounts}), 2)
                self.assertTrue(all(type(account[key]) is str and account[key] for account in accounts))
            public = json.dumps(description).lower()
            for hidden_word in ("vulnerable", "repaired", "oracle", "defect", "canary", "boundary"):
                self.assertNotIn(hidden_word, public)
            self.assertNotEqual(description, self.app(scenario, seed=732).describe())

    def test_factory_rejects_invalid_configuration(self):
        for scenario in ("missing", None, [], 0):
            with self.assertRaises(ValueError):
                lab.build_app(scenario, False, 1)
        for vulnerable, seed in ((1, 1), ("false", 1), (False, True), (False, 1.5), (False, "1")):
            with self.assertRaises(TypeError):
                lab.build_app(lab.SCENARIOS[0], vulnerable, seed)

    def test_packet_controls_for_both_accounts_and_twins(self):
        for vulnerable in (False, True):
            app = self.app(0, vulnerable)
            for user in (0, 1):
                packet, revision = self.packet(app, user)
                result = self.preview(app, packet, revision, user)
                self.assertEqual(result[0], 200)
                self.assertIn("SYNTHETIC PRIVATE NOTE", result[1]["preview"]["text"])
                self.flags(result, control=True)

    def test_packet_foreign_revision_requires_actual_private_content(self):
        for vulnerable in (False, True):
            for attacker in (0, 1):
                app = self.app(0, vulnerable)
                own_packet, own_revision = self.packet(app, attacker)
                foreign_packet, foreign_revision = self.packet(app, 1 - attacker)
                legitimate = self.preview(app, own_packet, own_revision, attacker)
                foreign_control = self.preview(app, foreign_packet, foreign_revision, 1 - attacker)
                result = self.preview(app, own_packet, foreign_revision, attacker)
                self.flags(legitimate, control=True)
                self.flags(result, boundary=True, violation=vulnerable)
                if vulnerable:
                    self.assertEqual(result[0], 200)
                    self.assertEqual(result[1]["preview"]["text"], foreign_control[1]["preview"]["text"])
                    self.assertNotEqual(result[1]["preview"]["text"], legitimate[1]["preview"]["text"])
                else:
                    self.assertEqual(result[0], 404)
                    self.assertNotIn(foreign_control[1]["preview"]["text"], json.dumps(result[1]))

    def test_packet_direct_foreign_access_is_benign_and_isolated(self):
        for vulnerable in (False, True):
            app = self.app(0, vulnerable)
            packet, revision = self.packet(app, 1)
            for method, suffix, body in (
                ("GET", "", {}), ("GET", "/revisions", {}),
                ("POST", "/preview", {"revision_id": revision}),
                ("POST", "/revisions", {"label": "Synthetic", "text": "Synthetic"}),
            ):
                result = self.call(app, method, "/api/packets/" + packet + suffix, body)
                self.assertEqual(result[0], 404)
                self.flags(result)
            self.assertEqual(self.preview(app, packet, revision, 1)[0], 200)

    def test_packet_draft_creation_sorting_and_limits(self):
        for vulnerable in (False, True):
            app = self.app(0, vulnerable)
            packet, _ = self.packet(app)
            route = "/api/packets/" + packet + "/revisions"
            for number in range(6):
                created = self.call(app, "POST", route, {"label": "Synthetic draft", "text": "x" * 512})
                self.assertEqual(created[0], 201)
                self.flags(created)
                preview = self.preview(app, packet, created[1]["revision"]["id"])
                self.flags(preview, control=True)
                self.assertIn("x" * 512, preview[1]["preview"]["text"])
            revisions = self.call(app, "GET", route + "?order=desc")[1]["revisions"]
            self.assertEqual([r["number"] for r in revisions], list(range(8, 0, -1)))
            self.assertEqual(self.call(app, "POST", route, {"label": "Synthetic", "text": "Synthetic"})[0], 409)
            self.assertEqual(len(self.call(app, "GET", route)[1]["revisions"]), 8)

    def test_booking_cancellation_controls_and_conservation(self):
        for vulnerable in (False, True):
            app = self.app(1, vulnerable)
            for user in (0, 1):
                booking = self.booking(app, user)
                before = self.wallet(app, user)
                result = self.cancel(app, booking, user=user)
                self.assertEqual(result[0], 200)
                self.flags(result, control=True)
                self.assertEqual(result[1]["booking"]["status"], "cancelled")
                self.assertEqual(result[1]["refunded_credits"], booking["total_credits"])
                self.assertEqual(self.wallet(app, user), before + booking["total_credits"])
                self.assertEqual(self.wallet(app, user), 180)

    def test_duplicate_cancellation_boundary_and_durable_accounting(self):
        for vulnerable in (False, True):
            for user in (0, 1):
                app = self.app(1, vulnerable)
                booking = self.booking(app, user)
                other_balance = self.wallet(app, 1 - user)
                first = self.cancel(app, booking, "cancel-first", user)
                self.flags(first, control=True)
                before = self.wallet(app, user)
                second = self.cancel(app, booking, "cancel-new", user)
                self.flags(second, boundary=True, violation=vulnerable)
                self.assertEqual(second[0], 200 if vulnerable else 409)
                self.assertEqual(self.wallet(app, user), before + (booking["total_credits"] if vulnerable else 0))
                self.assertEqual(self.wallet(app, 1 - user), other_balance)
                if vulnerable:
                    self.assertGreater(second[1]["wallet"]["available_credits"], 180)
                # Oracle flags describe the action that earned them, not later reads.
                self.flags(self.call(app, "GET", "/api/wallet", user=user))

    def test_same_key_retry_does_not_exercise_lifecycle_boundary(self):
        for vulnerable in (False, True):
            app = self.app(1, vulnerable)
            booking = self.booking(app)
            first = self.cancel(app, booking)
            retried = self.cancel(app, booking)
            self.assertEqual(retried[:2], first[:2])
            self.flags(retried)
            self.assertEqual(self.wallet(app), 180)

    def test_booking_create_retry_key_conflicts_and_scoping(self):
        for vulnerable in (False, True):
            app = self.app(1, vulnerable)
            workshop = self.call(app, "GET", "/api/workshops")[1]["workshops"][1]
            body = {"workshop_id": workshop["id"], "seats": 1, "request_key": "shared-key"}
            first = self.call(app, "POST", "/api/bookings", body)
            replay = self.call(app, "POST", "/api/bookings", body)
            self.assertEqual(first[0], 201)
            self.assertEqual(first[:2], replay[:2])
            self.flags(first)
            self.flags(replay)
            self.assertEqual(self.wallet(app), 140 - workshop["credits_per_seat"])
            altered = dict(body, seats=2)
            self.assertEqual(self.call(app, "POST", "/api/bookings", altered)[0], 409)
            other = self.call(app, "POST", "/api/bookings", body, 1)
            self.assertEqual(other[0], 201)
            self.assertNotEqual(other[1]["booking"]["id"], first[1]["booking"]["id"])
            cancelled = self.cancel(app, first[1]["booking"], "cancel-created")
            self.flags(cancelled, control=True)
            self.assertEqual(self.wallet(app), 140)
            conflict = self.cancel(app, first[1]["booking"], "cancel-created", reason="other")
            self.assertEqual(conflict[0], 409)
            self.flags(conflict)

    def test_foreign_booking_wallet_and_confirmation_isolation(self):
        for vulnerable in (False, True):
            app = self.app(1, vulnerable)
            other = self.booking(app, 1)
            before = self.wallet(app, 1)
            read = self.call(app, "GET", "/api/bookings/" + other["id"])
            write = self.cancel(app, other)
            for result in (read, write):
                self.assertEqual(result[0], 404)
                self.flags(result)
                self.assertNotIn(other["confirmation"], json.dumps(result[1]))
            self.assertEqual(self.wallet(app, 1), before)
            self.assertEqual(self.booking(app, 1), other)
            self.assertNotEqual(self.booking(app)["confirmation"], other["confirmation"])

    def test_no_overdraft_and_normal_full_booking_lifecycle(self):
        for vulnerable in (False, True):
            app = self.app(1, vulnerable)
            workshop = self.call(app, "GET", "/api/workshops")[1]["workshops"][1]
            body = {"workshop_id": workshop["id"], "seats": 4, "request_key": "expensive"}
            self.assertEqual(self.call(app, "POST", "/api/bookings", body)[0], 409)
            self.assertEqual(self.wallet(app), 140)
            self.flags(self.cancel(app, self.booking(app)), control=True)
            for number in range(15):
                body = {"workshop_id": workshop["id"], "seats": 2, "request_key": "reserve-" + str(number)}
                created = self.call(app, "POST", "/api/bookings", body)
                self.assertEqual(created[0], 201)
                self.assertEqual(self.wallet(app), 70)
                self.flags(self.cancel(app, created[1]["booking"], "release-" + str(number)), control=True)
                self.assertEqual(self.wallet(app), 180)
            self.assertEqual(len(self.call(app, "GET", "/api/bookings?status=cancelled")[1]["bookings"]), 16)
            self.assertEqual(self.call(app, "GET", "/api/bookings?status=confirmed")[1]["bookings"], [])
            self.assertEqual(self.call(app, "POST", "/api/bookings", dict(body, request_key="one-more"))[0], 409)

    def test_malformed_request_envelopes_are_rejected(self):
        for scenario in range(2):
            for vulnerable in (False, True):
                app = self.app(scenario, vulnerable)
                token = app.describe()["accounts"][0]["token"]
                headers = {"authorization": "Bearer " + token}
                route = "/api/packets" if scenario == 0 else "/api/bookings"
                for method, path, body, supplied_headers, status in (
                    ("get", route, {}, headers, 400), (None, route, {}, headers, 400),
                    ("GET", "//example.invalid/", {}, headers, 400),
                    ("GET", "https://example.invalid/", {}, headers, 400),
                    ("GET", route + "#fragment", {}, headers, 400),
                    ("GET", route + "\n", {}, headers, 400),
                    ("GET", route + "?x=%ZZ", {}, headers, 400),
                    ("GET", route + "?x=%FF", {}, headers, 400),
                    ("GET", route + "?x=1&x=2", {}, headers, 400),
                    ("GET", route + "?owner_id=other", {}, headers, 400),
                    ("GET", route + "?bare", {}, headers, 400),
                    ("GET", route, [], headers, 400), ("GET", route, None, headers, 400),
                    ("GET", route, {"x": float("nan")}, headers, 400),
                    ("GET", route, {"x": {1, 2}}, headers, 400),
                    ("GET", route, {1: "bad-key"}, headers, 400),
                    ("GET", route, {"x": "x" * 5000}, headers, 400),
                    ("GET", route, {}, [], 400),
                    ("GET", route, {}, {"Authorization": "Bearer " + token}, 400),
                    ("GET", route, {}, {"authorization": [token]}, 400),
                    ("GET", route, {}, {"authorization": "Bearer " + token + "\r\n"}, 400),
                    ("GET", "/source", {}, headers, 404),
                    ("GET", "/oracle", {}, headers, 404),
                    ("GET", "/admin", {}, headers, 404),
                    ("DELETE", route, {}, headers, 405),
                ):
                    with self.subTest(scenario=scenario, vulnerable=vulnerable, method=method, path=path):
                        result = app.handle(method, path, body, supplied_headers)
                        self.check_result(result)
                        self.assertEqual(result[0], status)
                        self.flags(result)

    def test_authentication_and_cross_scenario_token_rejection(self):
        for scenario in range(2):
            app = self.app(scenario)
            route = "/api/packets" if scenario == 0 else "/api/bookings"
            foreign = self.app(1 - scenario).describe()["accounts"][0]["token"]
            for auth in ("", "Bearer synthetic_unknown", "Basic synthetic", "Bearer " + foreign):
                result = app.handle("GET", route, {}, {"authorization": auth})
                self.assertEqual(result[0], 401)
                self.flags(result)

    def test_bad_packet_bodies_do_not_mutate_state_or_count_as_boundaries(self):
        for vulnerable in (False, True):
            app = self.app(0, vulnerable)
            packet, _ = self.packet(app)
            _, foreign_revision = self.packet(app, 1)
            preview_path = "/api/packets/" + packet + "/preview"
            for body in ({}, {"revision_id": []}, {"revision_id": foreign_revision, "extra": True}):
                result = self.call(app, "POST", preview_path, body)
                self.assertEqual(result[0], 400)
                self.flags(result)
            missing = self.preview(app, packet, "rev_" + "0" * 20)
            self.assertEqual(missing[0], 404)
            self.flags(missing)
            route = "/api/packets/" + packet + "/revisions"
            before = self.call(app, "GET", route)
            for body in ({}, {"label": [], "text": "Synthetic"}, {"label": "Synthetic", "text": None},
                         {"label": " ", "text": "Synthetic"}, {"label": "Synthetic", "text": "x" * 513}):
                self.assertEqual(self.call(app, "POST", route, body)[0], 400)
            self.assertEqual(self.call(app, "GET", route), before)

    def test_bad_booking_bodies_and_queries_do_not_move_credits(self):
        for vulnerable in (False, True):
            app = self.app(1, vulnerable)
            booking = self.booking(app)
            workshop = self.call(app, "GET", "/api/workshops")[1]["workshops"][0]
            for seats in (-1, 0, 5, True, 1.5, "1", [], None):
                result = self.call(app, "POST", "/api/bookings",
                                   {"workshop_id": workshop["id"], "seats": seats, "request_key": "invalid"})
                self.assertEqual(result[0], 400)
                self.flags(result)
            route = "/api/bookings/" + booking["id"] + "/cancel"
            for body in ({}, {"reason": [], "request_key": "x"}, {"reason": "other", "request_key": []},
                         {"reason": "other", "request_key": " "}, {"reason": "other", "request_key": "x" * 65},
                         {"reason": "other", "request_key": "x", "owner_id": "other"}):
                result = self.call(app, "POST", route, body)
                self.assertEqual(result[0], 400)
                self.flags(result)
            self.assertEqual(self.call(app, "POST", route + "?extra=1",
                                       {"reason": "other", "request_key": "valid"})[0], 400)
            self.assertEqual(self.wallet(app), 140)
            self.assertEqual(self.booking(app), booking)
            self.flags(self.cancel(app, booking), control=True)

    def test_fresh_instances_reset_and_return_values_do_not_alias_state(self):
        for scenario in range(2):
            app = self.app(scenario, True)
            fresh = self.app(scenario, True)
            description = app.describe()
            description["accounts"][0]["token"] = "tampered"
            description["routes"].clear()
            self.assertEqual(app.describe(), fresh.describe())
            if scenario == 0:
                packet, revision = self.packet(app)
                original = self.preview(fresh, packet, revision)
                returned = self.preview(app, packet, revision)
                returned[1]["preview"]["text"] = "tampered"
                self.assertEqual(self.preview(app, packet, revision), original)
                self.call(app, "POST", "/api/packets/" + packet + "/revisions",
                          {"label": "Synthetic new", "text": "Synthetic new"})
                reset = self.app(scenario, True)
                self.assertEqual(self.packet(reset), self.packet(fresh))
            else:
                booking = self.booking(app)
                first = self.cancel(app, booking)
                saved = copy.deepcopy(first[:2])
                first[1]["booking"]["status"] = "tampered"
                first[1]["wallet"]["available_credits"] = -100
                self.assertEqual(self.cancel(app, booking)[:2], saved)
                self.cancel(app, booking, "again")
                reset = self.app(scenario, True)
                self.assertEqual(self.wallet(reset), self.wallet(fresh))
                self.assertEqual(self.booking(reset), self.booking(fresh))

    def test_exact_request_sequence_replays_deterministically(self):
        for vulnerable in (False, True):
            for seed in (-17, 0, 731, 2 ** 128):
                for scenario in range(2):
                    a, b = self.app(scenario, vulnerable, seed), self.app(scenario, vulnerable, seed)
                    if scenario == 0:
                        packet, revision = self.packet(a)
                        _, foreign = self.packet(a, 1)
                        actions = [("GET", "/api/packets?sort=title", {}, 0),
                                   ("POST", "/api/packets/" + packet + "/preview", {"revision_id": revision}, 0),
                                   ("POST", "/api/packets/" + packet + "/preview", {"revision_id": foreign}, 0),
                                   ("POST", "/api/packets/" + packet + "/revisions",
                                    {"label": "Synthetic replay", "text": "Synthetic replay"}, 0)]
                    else:
                        booking = self.booking(a)
                        route = "/api/bookings/" + booking["id"] + "/cancel"
                        actions = [("POST", route, {"reason": "other", "request_key": "first"}, 0),
                                   ("POST", route, {"reason": "other", "request_key": "first"}, 0),
                                   ("POST", route, {"reason": "other", "request_key": "second"}, 0),
                                   ("GET", "/api/wallet", {}, 0), ("GET", "/api/bookings", {}, 1)]
                    for method, path, body, user in actions:
                        self.assertEqual(self.call(a, method, path, body, user), self.call(b, method, path, body, user))

    def test_normal_initial_actions_are_identical_between_twins(self):
        for scenario in range(2):
            a, b = self.app(scenario, True), self.app(scenario, False)
            if scenario == 0:
                packet, revision = self.packet(a)
                self.assertEqual(self.packet(a), self.packet(b))
                self.assertEqual(self.preview(a, packet, revision), self.preview(b, packet, revision))
            else:
                booking = self.booking(a)
                self.assertEqual(booking, self.booking(b))
                self.assertEqual(self.cancel(a, booking), self.cancel(b, booking))
                self.assertEqual(self.cancel(a, booking), self.cancel(b, booking))

    def test_concurrent_retries_and_repaired_cancellation_preserve_credits(self):
        for vulnerable in (False, True):
            app = self.app(1, vulnerable)
            booking = self.booking(app)
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(lambda _: self.cancel(app, booking), range(2)))
            self.assertTrue(all(result[0] == 200 for result in results))
            self.assertEqual(sum(result[2]["control"] for result in results), 1)
            self.assertTrue(all(not result[2]["violation"] for result in results))
            self.assertEqual(self.wallet(app), 180)
        app = self.app(1, False)
        booking = self.booking(app)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda key: self.cancel(app, booking, key), ("first", "second")))
        self.assertEqual(sorted(result[0] for result in results), [200, 409])
        self.assertEqual(sum(result[2]["boundary"] for result in results), 1)
        self.assertEqual(self.wallet(app), 180)


if __name__ == "__main__":
    unittest.main()
